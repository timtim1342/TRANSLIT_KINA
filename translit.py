from re import findall, sub

from os.path import join
from os import getcwd, listdir

from praatio import tgio
from praatio.praatio_scripts import alignBoundariesAcrossTiers

def all_textgrids():  # ищет все текстгриды
    textgrids_names = []
    tdir = join(getcwd(), 'cyrillic')
    dirs = listdir(tdir)
    for file in dirs:
        textgrids_names.extend(findall(r'(\b.+)\.[Tt]ext[Gg]rid\b', file))
    return textgrids_names

def open_tg(tgname):  # переносит грид сюда
    inputFN = join(getcwd(), 'cyrillic', tgname + '.TextGrid')
    try:
        tg = alignBoundariesAcrossTiers(inputFN, maxDifference=0.15)
    except:
        tg = tgio.openTextgrid(inputFN)
    return tg

def tg_tiers(tg):  # переносит слои
    tD = tg.tierDict
    transc_tier, transl_tier, note_tier = tD['1'], tD['2'], \
                                          tD['3']  # тут назвния слоев оригинального грида
    return transc_tier, transl_tier, note_tier


def translit_dict():  # делает словарь трансл
    with open('transl_dict.csv', 'r', encoding='UTF-8') as f:
        txt = f.read()
    txt_list = txt.split('\n')
    txt_list = [i.split(';') for i in txt_list]
    translit_dict = {i[0]:i[1] for i in txt_list if len(i) == 2 and i[0] != ''}
    translit_dict_cap = {}
    for key in translit_dict.keys(): #  ad capitals
        translit_dict_cap[key.capitalize()] = translit_dict[key].capitalize()
    translit_dict.update(translit_dict_cap)

    return translit_dict

def new_TG(name):
    tg = open_tg(name)
    final_tier = []
    tt, Tt, nt = tg_tiers(tg)
    transl_dict = translit_dict()
    tEL = tt.entryList


    for start, stop, label in tEL:  # создает шаблон с временными границами по слою с транскр
        russian = findall(r'\[R.*\]', label)
        label = label.lower()  # убрать, если нужны звглавные
        label = label.replace('=', '')  # костины =

        label = label.split()  # меняет ё ю я в начале слов
        for i in range(len(label)):
            if label[i].startswith('я'):
                label[i] = label[i].replace('я', 'ja', 1)
            elif label[i].startswith('ё'):
                label[i] = label[i].replace('ё', 'jo', 1)
            elif label[i].startswith('ю'):
                label[i] = label[i].replace('ю', 'ju', 1)
        label = ' '.join(label)

        for key in sorted(transl_dict.keys(), key = len, reverse=True):

            label = label.replace(key, transl_dict[key])  # транслитит

        if len(russian) > 0:
            print(label)
            russian_transl = findall(r'\[r.*\]', label)
            for i in range(len(russian)):
                label = label.replace(russian_transl[i], russian[i])

        final_tier.append([start, stop, label])

    new_Ttier = tt.new(entryList=final_tier)  # слой c лат
    tg = tgio.Textgrid()
    t_tier = tt  # слой с кир
    Tr_t = t_tier.new(name='speakerid_LTranscription-txt-rut')
    tg.addTier(new_Ttier)
    tg.addTier(Tr_t)
    tg.addTier(Tt)
    tg.addTier(nt)
    inputFN = join(getcwd(), 'latin', name + '.TextGrid')
    tg.save(inputFN)


def main():
    TGnames = all_textgrids()
    total_worforms_d = {}
    for name in TGnames:
        print(name)
        new_TG(name)  # new_TG_dial(name)


if __name__ == '__main__':
    main()

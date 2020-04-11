from googletrans import Translator

def translate_to(word,dest):
    translator=Translator()
    translations = translator.translate([word], dest=dest)
    return translations[0].text




# r = [
#     'имя существительное',
#         ['кошка', 'кот', 'кат', 'гусеничный трактор', 'животное семейства кошачьих',
#          'сварливая женщина', 'двойной треножник'],
#         [
#             ['кошка',
#                 ['cat', 'grapnel', 'grappling', 'grapple', 'gib', 'pussycat'],
#                 None, 0.23752081, None, 2
#             ],
#             ['кот',
#                 ['cat', 'tomcat', 'male cat', 'gib', 'he-cat'],
#                 None, 0.18211353, None, 1
#             ],
#             ['кат',
#                 ['cat']
#                 , None, 0.022794181, None, 1],
#             ['гусеничный трактор',
#                 ['caterpillar tractor', 'crawler', 'caterpillar', 'cat'],
#                 None, 2.2126158e-05
#             ],
#             ['животное семейства кошачьих',
#                 ['feline', 'cat'],
#                 None, 1.1125731e-05
#             ],
#             ['сварливая женщина',
#                 ['shrew', 'termagant', 'fury', 'rater', 'vixen', 'cat'],
#                 None, 1.1125731e-05
#             ],
#             ['двойной треножник',
#                 ['cat'],
#                 None, 1.1125731e-05]
#             ],
#     'cat', 1],
#     ['глагол',
#         ['блевать', 'бить плетью', 'брать якорь на кат', 'изрыгать'], [['блевать', ['barf', 'spew', 'cat', 'ralph', 'spue', 'fetch up'], None, 3.32153e-05], ['бить плетью', ['cat'], None, 1.67017e-05], ['брать якорь на кат', ['cat'], None, 1.1125731e-05], ['изрыгать', ['spew', 'belch', 'belch out', 'disgorge', 'belch forth', 'cat'], None, 1.1125731e-05]], 'cat', 2]
#
# def parse_out(out):
#         for i in out:
#             print(i[1])
#
# print(parse_out(r))
from googletrans import Translator

def translate_to(word,dest):
    translator=Translator()
    translations = translator.translate([word], dest=dest)
    return translations[0].text
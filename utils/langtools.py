import re

def extract_words(speech: str):
    """Extracts each word from a speech. Returns the words as a string.
    """
    # words shall all be lower case
    speech = speech.lower()
    # replace special characters as blanks -> extract only words
    speech = re.sub(r'[\.\?\+\-\/,;!:]', '', speech) #speech.replace('.', '').replace(',', '').replace('!', '').replace('?', '').replace(';', '').replace('-', '')
    # replace numbers as blanks -> extract only words
    speech = re.sub(r'[0-9]', '', speech)
    # replace double spaces '  ' as a single space ' '
    speech = speech.replace('  ', ' ')
    # remove spaces at the start and end
    speech = speech.strip()
    # return words
    return speech

def extract_sentences(speech: str):
    """Extracts sentences, defined as strings starting and ending at punctuation:
    'A quick brown fox, jumped over? A lazy dog.' -> ['a quick brown fox,', 'jumped over?', 'a lazy dog']
    All strings will be returned in lower case.
    """
    sentences = re.split(r'[\.\?\+\-\/,;!]', speech)
    # strip spaces
    sentences = [i.strip() for i in sentences]
    # lower case
    sentences = [i.lower() for i in sentences]
    # keep strings in the list only if their length is over 0 -> they have content.
    sentences = [i for i in sentences if len(i)>0]
    # return the list
    return sentences


#'A quick brown fox, jumped over? A lazy dog.'.split('[,]')
#re.split(r'[\.\?\+\-\/,;!:]', 'A quick brown fox, jumped over? A lazy dog.')
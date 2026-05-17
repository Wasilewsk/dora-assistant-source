# utils.py

def text_to_number(text):
    """
    Converts common English number words to digits.
    """
    number_map = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20'
    }
    
    # Check if the word is in our map
    word = text.lower().strip()
    if word in number_map:
        return number_map[word]
    
    # If it's already a digit, return it
    if word.isdigit():
        return word
        
    # If the text contains a digit somewhere, extract it
    import re
    digits = re.findall(r'\d+', word)
    if digits:
        return digits[0]
        
    return text

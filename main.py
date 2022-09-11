#выделение из текста только слов, приведение к нижнему регистру, сохранение их в список
import sys

if len(sys.argv)==2:
    input_dir=sys.argv[1]
    with open(input_dir) as f_input:
    list_data = f_input.read().split()
    for word in list_data:
        if type(word) =! str:
            delete word
        else:
            lower(word)

else:
    list_data = stdin.read().split()
    for word in list_data:
        if type(word) =! str:
            delete word
        else:
            lower(word)

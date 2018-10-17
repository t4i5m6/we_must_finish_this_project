import pandas as pd
import numpy as np
import jieba
'''
df = pd.read_excel(r'/home/anthony/Desktop/asus/201704全產品對話記錄_time.xlsx')
df = df[df.MessageType == 'text'].reset_index()
df['Content'] = df['Content'].str.upper()

df_customer = df.dropna().reset_index()'''

def separateUserContent(df_customer):

    # Separate different users' content 
    num_of_data = len(df_customer)
    all_customer_content = []

    previous_chatid = ""
    content_to_add = []
    for i in range(num_of_data):
        
        current_chatid = df_customer['ChatId'][i]
        if (current_chatid == previous_chatid):
            content_to_add.append(df_customer['Content'][i])
        # ID change    
        else:
            previous_chatid = current_chatid
            all_customer_content.append(content_to_add)
            content_to_add = []
            content_to_add.append(df_customer['Content'][i])           
    del(all_customer_content[0])
    return all_customer_content

def separateAllContent(df):
    # Separate all content 
    num_of_data = len(df)
    all_content = []
    all_link = []
    previous_chatid = ""
    content_to_add = []
    link_to_add = []

    for i in range(num_of_data):
        
        to_filter = ["歡迎使用", "系統公告", "系統宣告"] 
        if any(x in str(df['Content'][i]) for x in to_filter):
            continue
            
        if pd.isnull(df['Link'][i]):
            link = 's'
        else:
            link = 'c'
            
        current_chatid = df['ChatId'][i]
        if (current_chatid == previous_chatid):
            content_to_add.append(df['Content'][i])       
            link_to_add.append(link)       
        # ID change    
        else:
            previous_chatid = current_chatid
            all_content.append(content_to_add)
            all_link.append(link_to_add)
            content_to_add = []
            link_to_add = []
            content_to_add.append(df['Content'][i])   
            link_to_add.append(link)

    del(all_content[0])
    del(all_link[0])
    return all_content, all_link

def generateTVData(all_content, all_link):
    training_set = []
    validation_data_set = []

    for i in range(len(all_content)):
        tmp_list = []
        if i % 10 == 2:
            for j in range(len(all_content[i])):
                tup = (all_content[i][j], all_link[i][j])
                tmp_list.append(tup)
            validation_data_set.append(tmp_list)
        else:
            for j in range(len(all_content[i])):
                tup = (all_content[i][j], all_link[i][j])
                tmp_list.append(tup)
            training_set.append(tmp_list)

    return training_set, validation_data_set

def cutWords2Dict(training_set):
    # Using jieba

    # For TF total
    word_dictionary = {}

    # For later word2vec training
    corpus = []

    sum = 0
    for e1 in training_set:
        #print(e1)
        for e2 in e1:
            if e2[1] == 'c':
                corpus.append([' '.join(list(jieba.cut(str(e2[0]), cut_all=False)))])
                word_list = list(jieba.cut(str(e2[0]), cut_all=True))
                for word in word_list:
                    if word not in word_dictionary:
                        word_dictionary[word] = 1
                    else:
                        word_dictionary[word] = word_dictionary[word] + 1
        sum = sum + 1
        print("sum = ", sum)
    return word_dictionary, corpus
                

def filterLengthOneAndOutputTxt(word_dictionary, corpus):
    sor_r = sorted(word_dictionary.items(), key=lambda x:x[1], reverse=True)
    sor = sorted(word_dictionary.items(), key=lambda x:x[1], reverse=False)

    original_length = len(sor)
    new_sort = []
    new_sort_r = []
    for i in range(original_length):
        if len(sor[i][0]) > 1:
            new_sort.append(sor[i])
        if len(sor_r[i][0]) > 1:
            new_sort_r.append(sor_r[i])

    f1 = open("sort_one_word_remove.txt", "w")
    for t in new_sort:
        f1.write(' '.join(str(s) for s in t) + '\n')
    f1.close()    

    f2 = open("sort_one_word_remove_reverse.txt", "w")
    for t in new_sort_r:
        f2.write(' '.join(str(s) for s in t) + '\n')
    f2.close()    

    f3 = open("corpus.txt", "w")
    for t in corpus:
        f3.write(t[0])
        f3.write('\n')
    f3.close()        

def generateTrainTupleList():
	tmp_c = ""
	tmp_s = ""
	train_tup_list = []

	for small_list in training_set:
	    tmp_c = ""
	    tmp_s = ""
	    previous_status = ""
	    for tup in small_list:
	        if previous_status == "":
	            if tup[1] == 's':
	                continue
	            else:
	                tmp_c = str(tmp_c) + str(tup[0])
	                previous_status = 'c'
	        elif previous_status == 's':
	            # s -> s
	            if tup[1] == 's':
	                tmp_s = str(tmp_s) + " " + str(tup[0])
	            # s -> c
	            else:
	                train_tup_list.append((str(tmp_c), str(tmp_s)))
	                tmp_c = str(tup[0])
	                tmp_s = ""
	                previous_status = 'c'
	        else:
	            # c -> s
	            if tup[1] == 's':
	                tmp_s = str(tmp_s) + str(tup[0])
	                previous_status = 's'
	            # c -> c
	            else:
	                tmp_c = str(tmp_c) + " " + str(tup[0])
	    train_tup_list.append((str(tmp_c), str(tmp_s)))
	return train_tup_list

def generateValidationTupleList():
	tmp_c = ""
	tmp_s = ""
	tmp_tup = []
	validation_tup_list = []


	for small_list in validation_data_set:
	    tmp_c = ""
	    tmp_s = ""
	    previous_status = ""
	    for tup in small_list:
	        if previous_status == "":
	            if tup[1] == 's':
	                continue
	            else:
	                tmp_c = str(tmp_c) + str(tup[0])
	                previous_status = 'c'
	        elif previous_status == 's':
	            # s -> s
	            if tup[1] == 's':
	                tmp_s = str(tmp_s) + " " + str(tup[0])
	            # s -> c
	            else:
	                tmp_tup.append((str(tmp_c), str(tmp_s)))
	                tmp_c = str(tup[0])
	                tmp_s = ""
	                previous_status = 'c'
	        else:
	            # c -> s
	            if tup[1] == 's':
	                tmp_s = str(tmp_s) + str(tup[0])
	                previous_status = 's'
	            # c -> c
	            else:
	                tmp_c = str(tmp_c) + " " + str(tup[0])
	    tmp_tup.append((str(tmp_c), str(tmp_s)))
	    validation_tup_list.append(tmp_tup)
	    tmp_tup = []
	return validation_tup_list    
'''
all_customer_content = separateUserContent()
all_content, all_link = separateAllContent()

training_set, validation_data_set = generateTVData(all_content, all_link)

word_dictionary, corpus = cutWords2Dict(training_set)
filterLengthOneAndOutputTxt(word_dictionary, corpus)

train_tup_list = generateTrainTupleList()
validation_tup_list = generateValidationTupleList()'''
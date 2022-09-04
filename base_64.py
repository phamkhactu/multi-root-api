import base64
import tempfile
import sys, fitz
import docx
import re

TEXT = 0
PDF = 1
DOCX = 2
DOC =3
def isBase64(sb):
    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
        return False  
    
def get_raw_text(raw_text,file_type,page_from,page_to):
    if file_type == TEXT:
        return raw_text
    elif file_type == PDF or file_type == DOC or file_type == DOCX:
        ischeck =  isBase64(raw_text)
        if ischeck == True:
            temp = tempfile.NamedTemporaryFile()
            print("Created file is:", temp)
            print("Name of the file is:", temp.name)
            decode_raw =  base64.b64decode(raw_text)
            binary_file = open(temp.name, "wb")
            # Write bytes to file
            binary_file.write(decode_raw)
            if file_type == PDF:
                text = process_pdf_text(temp.name,page_from,page_to)
            else:
                text = process_doc_text(temp.name)
            return text
        else:
            return ''
    else:
        return ''

def process_pdf_text(file_name,page_from,page_to):
    doc = fitz.open(file_name)  # open document
    all_text = ''
    count = 0
    all_text_list_process = []
    stop_paragraph = ('...', '.', '?', '!', '!!!', ':')
    for page in doc:  # iterate the document pages
        if page.number >= page_from and page.number <= page_to:
            count+=1
            blocks = page.get_text("blocks")  # get plain text (is in UTF-8)
            # process into paragraph
            list_paragraph = []
            for b in blocks:
                temp_paragraph = re.split('\n\n| \n \n|\n \n',re.sub(' +', ' ', b[4]))
                for paragraph in temp_paragraph:
                    list_paragraph.append(paragraph)
            all_text_list = []
            for paragraph in list_paragraph:
                text = paragraph.replace("\n", " ") 
                strencode = text.encode("ascii", "ignore")
                #decode() method
                text = strencode.decode()
                text = text.replace("\t", "") 
                text = text.replace("\r", "") 
                re.sub('[^A-Za-z0-9]+', '', text)
                re.sub(' +', ' ', text)
                text = text.rstrip()
                text = text.strip()
                if '<image' in text:
                    continue
                if isinstance(re.search("Figure [0-9]", text), tuple) and re.search("Figure [0-9]", text).span()[0] == 0:
                    continue
                if isinstance(re.search("Table [0-9]", text), tuple) and re.search("Table [0-9]", text).span()[0] == 0:
                    continue
                all_text_list.append(text)
                # all_text_list_unprocess.append(text)
            for paragraph in all_text_list:
                # remove chu thich
                if len(paragraph.split(' ')) > 15:
                    if paragraph[0].isnumeric() == True :
                        if paragraph[1].isupper() == True:
                            continue
                        elif paragraph[1].isnumeric() == True:
                            if paragraph[2].isupper() == True:
                                continue
                            elif paragraph[2].isnumeric() == True:
                                if paragraph[3].isupper() == True:
                                    continue
                #             
                if len(paragraph.split(' ')) > 25 :
                    all_text_list_process.append(paragraph)
                elif len(paragraph.split(' ')) > 15 :
                    if paragraph[0].isupper() == True and paragraph[-1] in stop_paragraph:
                        continue
                    elif paragraph[0].isupper() == True or paragraph[-1] in stop_paragraph or (paragraph[-1].isnumeric() == True and paragraph[-2] in stop_paragraph):
                        all_text_list_process.append(paragraph)
                    elif paragraph[0].isupper() == True or paragraph[-1] in stop_paragraph or (paragraph[-1].isnumeric() == True and paragraph[-2].isnumeric()== True and paragraph[-3] in stop_paragraph):
                        all_text_list_process.append(paragraph)
                    elif paragraph[0].isupper() == True or paragraph[-1] in stop_paragraph or (paragraph[-1].isnumeric() == True and paragraph[-2].isnumeric()== True and paragraph[-3].isnumeric()== True and paragraph[-4] in stop_paragraph):
                        all_text_list_process.append(paragraph)
                else:
                    continue
    for idx, paragraph in enumerate(all_text_list_process):
        try:
            if paragraph[0].isupper() == True and paragraph[-1] in stop_paragraph:
                all_text  = all_text+'\n'+ all_text_list_process[idx]
            elif paragraph[0].isupper() == True and paragraph[-1].isalpha() == False and paragraph[-2] in stop_paragraph:
                all_text  = all_text+'\n'+ all_text_list_process[idx]
            elif paragraph[0].isupper() == True and  all_text_list_process[idx+1][0].isupper() == False and paragraph[-1] not in stop_paragraph:
                    if len(all_text_list_process[idx+1])!=0 and all_text_list_process[idx+1][0].isupper() == False and all_text_list_process[idx+1][-1] in stop_paragraph:
                        all_text_list_process[idx] = all_text_list_process[idx]+' '+all_text_list_process[idx+1]
                        all_text  = all_text+'\n'+ all_text_list_process[idx]
                        all_text_list_process.pop(idx+1)
                    elif len(all_text_list_process[idx+1])!=0 and all_text_list_process[idx+1][0].isupper() == False and all_text_list_process[idx+1][-2] in stop_paragraph and 6[idx+1][-1].isnumeric() == True:
                        all_text_list_process[idx] = all_text_list_process[idx]+' '+all_text_list_process[idx+1]
                        all_text  = all_text+'\n'+ all_text_list_process[idx]
                        all_text_list_process.pop(idx+1)
                    elif len(all_text_list_process[idx+1])!=0 and all_text_list_process[idx+1][0].isupper() == False and all_text_list_process[idx+1][-1].isnumeric() == True and all_text_list_process[idx+1][-2].isnumeric()== True and all_text_list_process[idx+1][-3] in stop_paragraph:
                        all_text_list_process[idx] = all_text_list_process[idx]+' '+all_text_list_process[idx+1]
                        all_text  = all_text+'\n'+ all_text_list_process[idx]
                        all_text_list_process.pop(idx+1)
                    elif len(all_text_list_process[idx+1])!=0 and all_text_list_process[idx+1][0].isupper() == False and all_text_list_process[idx+1][-1].isnumeric() == True and all_text_list_process[idx+1][-2].isnumeric()== True and all_text_list_process[idx+1][-3].isnumeric()== True and all_text_list_process[idx+1][-4] in stop_paragraph:
                        all_text_list_process[idx] = all_text_list_process[idx]+' '+all_text_list_process[idx+1]
                        all_text  = all_text+'\n'+ all_text_list_process[idx]
                        all_text_list_process.pop(idx+1)
        except:
            continue
    return all_text
def process_doc_text(file_name):
    doc = docx.Document(file_name)
    all_paras = doc.paragraphs
    all_text = ''
    for para in all_paras:
        text = re.sub(' +', ' ', para.text)
        text = text.replace('\t',"")
        strencode = text.encode("ascii", "ignore")
            #decode() method
        text = strencode.decode()
        if get_length(text) > 25:
            all_text = all_text +'\n'+text
    return all_text

def get_length(raw_text):
    word_list = raw_text.split()
    number_of_words = len(word_list)
    return number_of_words

if __name__ =="__main__":
    # raw_text = 'encode base 64 web gui sang'
    with open("encoded-20220727080145.txt", "r") as r:
        raw_text = r.read()
    # file_type = 'loai file'
    file_type = 1
    # page_from =  'bat dau tu trang'
    page_from =  0
    # page_to = 'trang ket thuc '
    page_to = 2
    print(get_raw_text(raw_text,file_type,page_from,page_to))
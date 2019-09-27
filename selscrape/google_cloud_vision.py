'''
Created on Feb 25, 2018

$ base64 -i downloads/duval.jpg -o duval.txt
$ bash gcv.sh gcv_duval.json > tttt.txt

To Run from command line:

image_path='./duval.jpg'
request_json_out='./gcv_duval_request.json'
response_json_out='./gcv_duval_repsonse.json'
csv_out='./gcv_duval.csv'
api_key='AIzaSyCUeeA0G23vE5aMAQRyfOpPrxnFK9-37FQ'
python google_cloud_vision.py ${image_path}   ${request_json_out} ${response_json_out} ${csv_out} ${api_key}

@author: bperlman1
'''
import urllib.request
import base64
import json
import pandas as pd
import sys

def postit(url,json_data,json_headers=None,timeout_value=None):
    headers = json_headers
    if headers is None:
        headers = {}
    request = urllib.request.Request(url, json_data.encode(), headers)
    timeout = timeout_value
    if timeout is None:
        timeout = 30
    f = urllib.request.urlopen(request, timeout=timeout)
    response = f.read()
    parsed = json.loads(response)
    return parsed

def create_base64AttachmentText(blob_string):
    base64AttachmentText = base64.b64encode(blob_string)
    return base64AttachmentText.decode("utf-8")

def pdf_to_base64_text(pdf_path):
    blob_string = open(pdf_path,'rb').read()
    b64_text =  create_base64AttachmentText(blob_string)
    return b64_text


class GoogleCloudVision():
    def __init__(self,api_key):
        self.header = {'Content-type': 'application/json'}
        self.url = 'https://vision.googleapis.com/v1/images:annotate?key=%(API_KEY)s' %{'API_KEY':api_key}
        

    def get_json_data(self,encoded_text):
        return_json = {
                              "requests":
                              [
                                {
                                  "image":{"content": encoded_text},
                                  "features": [{"type":"TEXT_DETECTION"}]
                                }
                              ]
                            }
        return return_json

    def get_json_data_encoded(self,encoded_text):
        return_json = self.get_json_data(encoded_text)
        return json.dumps(return_json)
    
    def get_gcv_request_json(self,pdf_path):
        encoded_text = pdf_to_base64_text(pdf_path)
        json_data = self.get_json_data(encoded_text)
        return json_data

    def get_gcv_text(self,pdf_path):
        encoded_text = pdf_to_base64_text(pdf_path)
        json_data = self.get_json_data_encoded(encoded_text)
        json_response = postit(self.url, json_data, self.header)
        return json_response

    def parse_json_response(self,json_response):
        array_text_annotation_json = json_response['responses'][0]['textAnnotations']
        description_array = []
        upper_left_x_array = []
        upper_left_y_array = []
        lower_left_x_array = []
        lower_left_y_array = []
        upper_right_x_array = []
        upper_right_y_array = []
        lower_right_x_array = []
        lower_right_y_array = []
        for text_annotation_json in array_text_annotation_json:
            description_array.append(text_annotation_json['description'])
            vertices = text_annotation_json['boundingPoly']['vertices']
            upper_left_x_array.append(vertices[0]['x'])
            upper_left_y_array.append(vertices[0]['y'])
            upper_right_x_array.append(vertices[1]['x'])
            upper_right_y_array.append(vertices[1]['y'])
            lower_right_x_array.append(vertices[2]['x'])
            lower_right_y_array.append(vertices[2]['y'])
            lower_left_x_array.append(vertices[3]['x'])
            lower_left_y_array.append(vertices[3]['y'])
            
        df = pd.DataFrame({
                           'ulx':upper_left_x_array,
                           'uly':upper_left_y_array,
                           'urx':upper_right_x_array,
                           'ury':upper_right_y_array,
                           'llx':lower_left_x_array,
                           'lly':lower_left_y_array,
                           'lrx':lower_right_x_array,
                           'lry':lower_right_y_array,
                           'text':description_array
                           })
        return df
        
        
if __name__=="__main__":
    '''
    To Run from command line:
    python google_cloud_vision.py './duval.jpg'  './gcv_duval_request.json' './gcv_duval_repsonse.json' gcv_duval.csv
    '''
    try:
        image_path = sys.argv[1]
        json_request_path = sys.argv[2]
        json_response_path = sys.argv[3]
        dataframe_out_path = sys.argv[4]
        api_key = sys.argv[5]
    except:
        print('missing arguments')
        print('to run: python google_cloud_vision.py image_path json_request_path json_response_path dataframe_out_path api_key')
        sys.exit(-1)
        
#     api_key = "AIzaSyCUeeA0G23vE5aMAQRyfOpPrxnFK9-37FQ"
    gcv = GoogleCloudVision(api_key)
    json_request = gcv.get_gcv_request_json(image_path)
    json.dump(json_request,open(json_request_path,'w'))
    json_response = gcv.get_gcv_text(image_path)
    json.dump(json_response,open(json_response_path,'w'))    
    df = gcv.parse_json_response(json_response)    
    print(df)   
    df.to_csv(dataframe_out_path,index=False)
    json
    
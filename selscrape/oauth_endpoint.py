'''
Created on Mar 17, 2017

@author: bperlman1
'''
import arg_access
import flask as fl
from flask import make_response
from flask import send_file
import StringIO as sio
import pandas as pd
import box_access as bacc
import selaccess_dummy as dum
import sel_access as selacc
# import sys
# import pycurl
import os
import glob

BOX_CONFIG_FILE_PATH = ''
# Initialize the Flask application
app = fl.Flask(__name__)
app.secret_key = 'development key'

# Route that will process the file upload
@app.route('/get_authorization_url', methods=['GET','POST'])
def get_authorization_url():
    # get code
    code = fl.request.args.get('code')
    print "writing code %s" %(str(code))
    open('oauth_code.txt','w').write(str(code))
    div = '<div id="code">' + str(code)+'</div>'
    return fl.render_template('default.html', html_to_display=div)

@app.route('/merge_pdfs', methods=['GET','POST'])
def merge_pdfs():
    global BOX_CONFIG_FILE_PATH
    url_list_string = fl.request.args.get('url_list_string')
    this_folder = selacc.get_full_path_of_import(dum)
    temp_folder = this_folder + "/temp_folder/pdf_merge"
    for f in glob.glob(temp_folder + "/*.pdf"):
        os.remove(f)
        
    url_list = url_list_string.split(",")
    filename_list = []
    for i in range(len(url_list)):
        url = url_list[i]
        filename = temp_folder + "/temp_" + str(i) + '.pdf'
        filename_list.append(filename) 
        os.system('curl -o ' + filename + " " + url)
#         fp = open(filename, "wb")
#         curl = pycurl.Curl()
#         curl.setopt(pycurl.URL, url)
#         curl.setopt(pycurl.WRITEDATA, fp)
#         curl.perform()
#         curl.close()
#         fp.close() 
           
    filename_string = ' '.join(filename_list)
    merge_path = temp_folder + "/temp_merge_file.pdf" 
    d = {'_THIS_FOLDER':this_folder,'_FILENAME_STRING':filename_string,'_MERGE_PATH':merge_path}
    pdf_box_cmd = "java -jar  %(_THIS_FOLDER)s/pdfbox-app-2.0.5.jar  PDFMerger %(_FILENAME_STRING)s %(_MERGE_PATH)s" %d
    os.system(pdf_box_cmd)
#     return workato_return(pd.DataFrame({'status':['0']}))
    destination_file = fl.request.args.get('destination_file')
    destination_folder = fl.request.args.get('destination_folder')
    bac = bacc.BoxAccess(BOX_CONFIG_FILE_PATH)
    client = bac.get_client()
    f =  bac.find_folder_from_root(client, destination_folder)
     
    box_file = client.folder(f.id).upload(merge_path, destination_file)
    df = pd.DataFrame({'status':[str(box_file)]})
    return workato_return(df)
    
def workato_return(df):
    """
    This method will create an http response variable that can be used to return from a route.
    If return_json = true, then the response will be a json object as follows (assume that 215 csv lines, including the header, are returned:
        {"result":
            {
                "0":"active_parcel,record_id,update_id,upf_ltd",
                "1":"2009-0178-0000-0019-0000,668681,1515891000540,130.00",
                "2":"2009-0178-0000-0019-0000,663672,1515890999758,1221.00",
                "3":"2009-0178-0000-0019-0000,648645,1515890994821,3878.22",
                ...
                "214":"2009-0178-0000-0019-0000,648645,1515890994821,3878.22"
            }
        }
    
    If return_zip = true, a zip file of the inner csv will be returned
    
    otherwise, the csv file will be returned 

    :param df:
    """
    # return a csv of the Dataframe
    return_zip = fl.request.args.get('return_zip')
    if return_zip is not None:
        # df_for_workato is really a memory_file of io.BytesIO()
        memory_file = df
        memory_file.seek(0)
        return send_file(memory_file, attachment_filename=return_zip, as_attachment=True)


    return_json = fl.request.args.get('return_json')
    if return_json is not None and str(return_json).lower()=='true':
        # create string array imbedded in DataFrame for workato csv return
        s = sio.StringIO()
        df.to_csv(s,index=False)
        arr = s.getvalue().split('\n')    
        df_for_workato =  pd.DataFrame({'result':arr})
        s = sio.StringIO()
        df_for_workato.to_json(s)
    else:
        s = sio.StringIO()
        df.to_csv(s,index=False)
    records_string = s.getvalue()
    
    output = make_response(records_string)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

def app_run(bcp,ip=None,port=None):
    global app
    global BOX_CONFIG_FILE_PATH
    BOX_CONFIG_FILE_PATH = bcp
    ip_to_use = ip
    port_to_use = port
    if ip_to_use is None:
        ip_to_use = '127.0.0.1'
    if port_to_use is None:
        port_to_use = 7111
    try:
        app.run(
            host=ip_to_use,
            port=int(str(port_to_use)),
            debug=False
        )
    except Exception,e:
        print str(e)

if __name__=="__main__":
    parser = arg_access.gpar()
    parser.add_argument('--config_file_path',
                        help='path to config file for Box login',type=str)
    args = parser.parse_args()
    
    box_config_path = args.config_file_path
    app_run(box_config_path)
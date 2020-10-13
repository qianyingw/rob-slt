#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 20:25:50 2020

@author: qwang
"""


import streamlit as st
# import pandas as pd
# import numpy as np
import re
import io
# import os
# import glob

from pred import pred_prob, pred_prob_bert, extract_sents
from pyxpdf import Document

#%%
p_ref = re.compile(r"(.*Reference\s{0,}\n)|(.*References\s{0,}\n)|(.*Reference list\s{0,}\n)|(.*REFERENCE\s{0,}\n)|(.*REFERENCES\s{0,}\n)|(.*REFERENCE LIST\s{0,}\n)", 
                   flags=re.DOTALL)

PROB_PATH = {
    'arg-r': 'pth/awr_13.json',
    'pth-r': 'pth/awr_13.pth.tar',
    'fld-r': 'fld/awr_13.Field',
    
    'arg-b': 'pth/awb_32.json',
    'pth-b': 'pth/awb_32.pth.tar',
    'fld-b': 'fld/awb_32.Field',
    
    'arg-i': 'pth/cwi_6.json',
    'pth-i': 'pth/cwi_6.pth.tar',
    'fld-i': 'fld/cwi_6.Field',
    
    'arg-w': 'pth/bert_w0.json',
    'pth-w': 'bert_w0.pth.tar',
    # 'wgt-w': 'pth/biobert',
    
    'arg-e': 'pth/awe_8.json',
    'pth-e': 'pth/awe_8.pth.tar',
    'fld-e': 'fld/awe_8.Field',
}
SENT_PATH = {
    'arg-r': 'pth/hr_4.json',
    'pth-r': 'pth/hr_4.pth.tar',
    'fld-r': 'fld/hr_4.Field',
    
    'arg-b': 'pth/hb_5.json',
    'pth-b': 'pth/hb_5.pth.tar',
    'fld-b': 'fld/hb_5.Field',
    
    'arg-i': 'pth/hi_4.json',
    'pth-i': 'pth/hi_4.pth.tar',
    'fld-i': 'fld/hi_4.Field',
    
    'arg-w': 'pth/hw_17.json',
    'pth-w': 'pth/hw_17.pth.tar',
    'fld-w': 'fld/hw_17.Field',
    
    'arg-e': 'pth/he_26.json',
    'pth-e': 'pth/he_26.pth.tar',
    'fld-e': 'fld/he_26.Field'
}
    

#%%
class SinglePredictor():
    
    def __init__(self, prob_path, sent_path):  
        
        self.prob_path = prob_path
        self.sent_path = sent_path
          
    def process_text(self, text):
        # Remove emtpy lines
        text = re.sub(r"^(?:[\t ]*(?:\r?\n|\r))+", " ", text, flags=re.MULTILINE)
        # Remove non-ascii characters
        text = text.encode("ascii", errors="ignore").decode()     
        # Strip whitespaces 
        text = re.sub(r'\s+', " ", text)
        # Remove the whitespace at start and end of line
        text = re.sub(r'^[\s]', "", text)
        text = re.sub(r'[\s]$', "", text)
        self.text = text
            
    def pred_probs(self):   
        text = self.text
        pr = pred_prob(self.prob_path['arg-r'], self.prob_path['fld-r'], self.prob_path['pth-r'], text).astype(float)
        pb = pred_prob(self.prob_path['arg-b'], self.prob_path['fld-b'], self.prob_path['pth-b'], text).astype(float)
        pi = pred_prob(self.prob_path['arg-i'], self.prob_path['fld-i'], self.prob_path['pth-i'], text).astype(float)
        pw = pred_prob_bert(self.prob_path['arg-w'], self.prob_path['pth-w'], text).astype(float)
        pe = pred_prob(self.prob_path['arg-e'], self.prob_path['fld-e'], self.prob_path['pth-e'], text).astype(float)     
        
        probs = {"random": pr, "blind": pb, "interest": pi, "welfare": pw, "exclusion": pe}   
        return probs
                        
    def get_sents(self, num_sents):
        text = self.text
        sr = extract_sents(self.sent_path['arg-r'], self.sent_path['fld-r'], self.sent_path['pth-r'], text, num_sents)
        sb = extract_sents(self.sent_path['arg-b'], self.sent_path['fld-b'], self.sent_path['pth-b'], text, num_sents)
        si = extract_sents(self.sent_path['arg-i'], self.sent_path['fld-i'], self.sent_path['pth-i'], text, num_sents)
        sw = extract_sents(self.sent_path['arg-w'], self.sent_path['fld-w'], self.sent_path['pth-w'], text, num_sents)
        se = extract_sents(self.sent_path['arg-e'], self.sent_path['fld-e'], self.sent_path['pth-e'], text, num_sents)

        sents = {"Random Allocation to Treatment/Control Group": sr, 
                 "Blinded Assessment of Outcome": sb, 
                 "Conflict of Interest": si, 
                 "Animal Welfare Regulations": sw, 
                 "Animal Exclusions": se}      
        return sents  


#%% App
st.write("""
# Risk of bias reporting for preclinical text
This app can predict the probabilities of risk of bias reporting for text from a preclinical paper. For batch processing and relevant sentences extraction, please check the [repository](https://github.com/qianyingw/rob-pome).
""")

upload_file = st.file_uploader("Upload your .txt or .pdf file", type=['txt', 'pdf'])

if upload_file:

    if isinstance(upload_file, io.StringIO):
        text = upload_file.read()  
    if isinstance(upload_file, io.BytesIO):
        doc = Document(upload_file)
        text = doc.text()
        # Remove texts before the first occurence of 'Introduction' or 'INTRODUCTION'
        text = re.sub(r".*?(Introduction|INTRODUCTION)\s{0,}\n{1,}", " ", text, count=1, flags=re.DOTALL)    
        # Remove reference after the last occurence 
        s = re.search(p_ref, text)
        if s: text = s[0]  
   
    rober = SinglePredictor(prob_path = PROB_PATH, sent_path = SENT_PATH)
    rober.process_text(text)
    
    with st.spinner('Predicting...'):
        probs = rober.pred_probs()
    st.success("""
                ### **Reporting probabilities: ** ###
    """)
    
    st.write("""
    - Random Allocation to Treatment/Control Group: 
    """, float("{:.6f}".format(probs['random'])))
    
    st.write("""
    - Blinded Assessment of Outcome: 
    """, float("{:.6f}".format(probs['blind'])))  
    
    st.write("""
    - Conflict of Interest: 
    """, float("{:.6f}".format(probs['interest'])))  
    
    st.write("""
    - Animal Welfare Regulations: 
    """, float("{:.6f}".format(probs['welfare'])))  
    
    st.write("""
    - Animal Exclusions: 
    """, float("{:.6f}".format(probs['exclusion'])))  
    
    # with st.spinner('Extracting sentences...'):
    #     sents = rober.get_sents(3)
    # st.success("""
    #            ### **Potential relevant sentences: ** ###
    # """)

    # st.write(sents) 
    
else:
    # with open('sample/Minwoo A, 2015.txt', 'r', encoding='utf-8', errors='ignore') as fin:
    #     text = fin.read() 
    st.write("""
              ### **Reporting probabilities of the [example TXT file](https://raw.githubusercontent.com/qianyingw/rob-pome/master/rob-app/sample/Minwoo%20A%2C%202015.txt)** ###
              """)

    st.write("""
             Random Allocation to Treatment/Control Group:
    """, 0.999992)
    
    st.write("""
     Blinded Assessment of Outcome: 
    """, 1e-06)  
    
    st.write("""
     Conflict of Interest: 
    """, 0.578319)  
    
    st.write("""
     Animal Welfare Regulations: 
    """, 0.373221)  
    
    st.write("""
     Animal Exclusions: 
    """, 0.190107)  
    
    sents = {
      "Random Allocation to Treatment/Control Group": [
        "In protocol 1, animals were randomly divided into two groups : saline control and losartan (Sigma, 10 mg / kg / day) treatment, continuously administered by osmotic pumps (Alzet model 2ML4, Durect Co) at 60 l / day for 14 days.",
        "The hearts were then isolated and treated with ischemia and reperfusion (IR) in the absence of losartan in the perfusate.",
        "In protocol 2, animals were treated with saline or losartan for 14 days, and the hearts were treated with IR in the continuous presence of losartan (1 mol / L) in the perfusate."
      ],
      "Blinded Assessment of Outcome": [
        "Briefly, RNA was isolated from left ventricles and cDNA for mature miR profiling was prepared using the miScript II RT kit.",
        "After 14 days of treatment, hearts were isolated for functional studies and protein and miR measurements.",
        "The present study demonstrates that in vivo chronic AT1R blockade with losartan leads to a significant increase in AT1R and PKC protein expression as well as an ischemic-sensitive signature of miR expression in the left ventricle, resulting in an increase in the heart vulnerability to acute onset of ischemic and reperfusion injury and a decrease in post-ischemic left ventricular function recovery in an isolated heart preparation."
      ],
      "Conflict of Interest": [
        "Heart disease is the leading cause of morbidity and mortality in the United States.",
        "Nonetheless, the effect of chronic AT1R blockade on the heart sensitivity to acute onset of ischemic injury in females remains to be determined.",
        "Briefly, RNA was isolated from left ventricles and cDNA for mature miR profiling was prepared using the miScript II RT kit."
      ],
      "Animal Welfare Regulations": [
        "Heart disease is the leading cause of morbidity and mortality in the United States.",
        "In addition to other risk factors, clinical and animal studies have shown an association between angiotensin II receptor (ATR) expression on cardiomyocytes and increased risk of ischemic heart disease and reduced cardiac recovery after ischemic injury [1\u00135].",
        "The heart may experience prolonged ischemia under a variety of conditions, including cardiomyopathy, endothelial dysfunction and coronary arterial disease, valvular dysfunction and hypotension."
      ],
      "Animal Exclusions": [
        "Given that remote ischemic preconditioning (RIPC) has clinical potential to minimize myocardial infarction in patients with high risk [53] and that RIPC mediates protection indirectly via remote humoral conditioning including adenosine, bradykinin, opioids, and HIF but minimal correlation with AT1R [54, 55]",
        "Consistent with these findings, there were no significant differences in myocardial infarct size and LVEDP between the two groups (Fig 7).",
        "In perspective of clinical significance, inhibition of AT1R is an important pharmacological therapy in the management of hypertension, particularly with long-term benefits in the treatment of patients in post-myocardial infarction period and at risk for ischemic heart disease."
      ]
    } 

    st.write("""
    ### **Potential relevant sentences: ** ###
    """) 
    st.write(sents) 

print('Finish')
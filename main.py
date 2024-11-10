import streamlit as st
import numpy as np
import pandas as pd

import os
from modules.settings.config_manager import config
config.load_settings(os.path.dirname(os.path.abspath(__file__)))
    
from modules.gmap_crawler import craw_hotel
from modules.data_handler import DataHandler

if __name__ == '__main__':
    
    st.title('評論分析網')

    hotel_name = st.text_input('請輸入欲查詢之飯店名稱')
    
    if st.button('生成評論分析報表'):
        data = craw_hotel(hotel_name)
        
        st.divider()
        st.header("飯店資訊", divider='red')
        st.markdown(f"**Hotel**: {data['name']}")
        st.markdown(f"**Star** : {data['star']}")
        st.markdown(f"**Rank** : {data['rank']}")
        st.markdown(f"**Address**: {data['information'].get('address', '---')}")
        st.markdown(f"**URL**  : {data['information'].get('url', '---')}")
        st.markdown(f"**Phone**: {data['information'].get('phone', '---')}")
        if data['information'].get('time'):
            st.markdown(f"**Check In**: {data['information']['time'].get('start', '---')}")
            st.markdown(f"**Check Out**: {data['information']['time'].get('end', '---')}")

        st.subheader("原始資料", divider=True)
        
        handler = DataHandler(data['review'])
        st.dataframe(handler.df, use_container_width=True)
        
        handler.exec_clean('comment')
        st.subheader("清理資料", divider=True)
        st.dataframe(handler.df, use_container_width=True)
        
        st.divider()
        st.markdown('''
                    :red[分析資料會耗時較久, 請耐心等候]
                    ''')
        handler.exec_analyze('comment')
        st.subheader("分析資料", divider=True)
        formed_df = pd.DataFrame(handler.formed_data)
        st.dataframe(formed_df, use_container_width=True)
        
        

from functools import reduce
import streamlit as st
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rc('font', family='Microsoft YaHei') #? 設定 中文顯示字體

import os
import time

from modules.settings.config_manager import config
config.load_settings(os.path.dirname(os.path.abspath(__file__)))
from modules.review_analizer import analyzer
    
from modules.gmap_crawler import craw_hotel
from modules.data_handler import DataHandler

from modules.db_manager import db

if __name__ == '__main__':
    st.title('評論分析網')
    
    st.text_input('請輸入欲查詢之飯店名稱', key='hotel_name')
    
    if st.button('生成評論分析報表') or st.session_state.hotel_name:
        st.divider()
        
        with st.status("執行評論爬蟲中，請稍後...", expanded=True) as crawler_status:
            start = time.time()
            
            #* keep data to prevent rerun affect
            if 'data_name' not in st.session_state or st.session_state.data_name != st.session_state.hotel_name:
                
                #* check hotel has been crawler before
                hotel_data = db.check_hotel_exist(st.session_state.hotel_name)
                if hotel_data:
                    data = hotel_data   #? using db data | do not have key: review
                    st.session_state['db_hotel_id'] = hotel_data.get('id')     #? mark for db render workflow
                      
                    #* delete original workflow
                    if 'hotel_id' in st.session_state:  
                        del st.session_state['hotel_id']
                        
                else:
                    data = craw_hotel(st.session_state.hotel_name)
                    st.session_state['hotel_id'] = db.insert_hotel(st.session_state.hotel_name, data)   #? mark for original data
                    
                    #* delete db workflow
                    if 'db_hotel_id' in st.session_state:
                        del st.session_state['db_hotel_id']
                        
                #* set hotel name -> data_name | crawler data -> hotel_data
                st.session_state.data_name = st.session_state.hotel_name
            
            else:
                #* check hotel has been crawler before
                hotel_data = db.check_hotel_exist(st.session_state.hotel_name)
                if hotel_data:
                    data = hotel_data   #? using db data | do not have key: review
                    st.session_state['db_hotel_id'] = hotel_data.get('id')     #? mark for db render workflow
                      
                    #* delete original workflow
                    if 'hotel_id' in st.session_state:  
                        del st.session_state['hotel_id']
            
            # === Information ===
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

            # === Table ===
            
            #* hotel data is not from db 
            if 'hotel_id' in st.session_state:
                st.subheader("原始資料", divider=True)
                handler = DataHandler(data['review'])
                st.dataframe(handler.df, use_container_width=True)
        
                handler.exec_clean('comment')
                st.subheader("清理資料", divider=True)
                st.dataframe(handler.df, use_container_width=True)
                
                for review_row in handler.df.to_dict(orient='records'):
                    db.insert_reviews(st.session_state['hotel_id'], review_row)

                data_length = len(data['review'])
                
            else:
                clean_data = db.get_hotel_reviews(st.session_state['db_hotel_id'])
                data_length = len(clean_data)
                
                st.subheader("清理資料", divider=True)
                st.dataframe(clean_data, use_container_width=True)
                

            # === Time Cost ===
            if st.session_state.data_name == st.session_state.hotel_name:
                st.markdown(f"**爬蟲耗時**: :red[{time.time() - start}] s, 共 :green[{data_length}] 筆評論")
            
            crawler_status.update(
                label="評論爬蟲完成", state="complete", expanded=True
            )
        
        with st.status("執行評論分析，分析耗時較久，請耐心等候...") as analyze_status:
            start = time.time()
            
            #* keep data to prevent rerun affect
            if 'analyze_name' not in st.session_state or st.session_state.analyze_name != st.session_state.hotel_name:
                
                if 'hotel_id' in st.session_state:
                    #> call open ai api to analyze reviews
                    handler.exec_analyze('comment')
                    end_analyze = time.time()
                    
                    formed_data = handler.formed_data
                    formed_file = config.dir.save_formed_file(st.session_state['hotel_id'],
                                                              formed_data)
                    db.insert_formed_record(st.session_state['hotel_id'], formed_file)
                
                else:
                    formed_file = db.get_formed_file(st.session_state['db_hotel_id'])
                    formed_data = config.dir.read_formed_file(formed_file)
                    
                #* set hotel name -> analyze_name | formed data -> analyze_data
                st.session_state.analyze_name = st.session_state.hotel_name
                st.session_state.analyze_data = formed_data
            
            else:
                #* reuse storaged data
                formed_data = st.session_state.analyze_data

            # === Parse formed data to tables ===
            if 'hotel_id' in st.session_state:
                st.subheader("分析資料", divider=True)
                formed_df = pd.DataFrame(formed_data)
                st.dataframe(formed_df, use_container_width=True)

                #> 關鍵字統計
                calc_result = analyzer.parse_key_words(formed_data)
            
                positive_counter = calc_result.get('positive')
                negative_counter = calc_result.get('negative')
                summary_counter  = calc_result.get('summary')
                
                db.insert_keycounts(st.session_state['hotel_id'], calc_result)
            
            else:
                calc_result = db.get_keycounts(st.session_state['db_hotel_id'])
        
                positive_counter = calc_result.get('positive')
                negative_counter = calc_result.get('negative')
                summary_counter  = calc_result.get('summary')
                
            # 只保留關鍵字被提及超過一次的
            positive_counter = analyzer.filter_freq(positive_counter, 1)
            negative_counter = analyzer.filter_freq(negative_counter, 1)
            
            if 'hotel_id' in st.session_state:
                # 解析數據成表格
                filterd_key = {
                    'positive': positive_counter.keys(),
                    'negative': negative_counter.keys()
                }
                
                spec_data = analyzer.parse_data_to_db_spec(formed_data, filterd_key)

                for spec_data_row in spec_data:
                    db.insert_analyzes(st.session_state['hotel_id'], spec_data_row)
            
            else:
                spec_data = db.get_hotel_analyzes(st.session_state['db_hotel_id'])
            
            data_list = analyzer.build_table(spec_data)
            # 取得 關鍵字 名字與顏色 對照表
            summary_options  = analyzer.build_multi_select_option(summary_counter.keys())
            positive_options = analyzer.build_multi_select_option(positive_counter.keys())
            negative_options = analyzer.build_multi_select_option(negative_counter.keys())

            # 顯示關鍵字保留選項
            positive_content = "**正面關鍵字**"
            for option in positive_options:
                positive_content += f" :{option['color']}[{option['name']}]"
            st.markdown(positive_content)
            
            negative_content = "**負面關鍵字**"
            for option in negative_options:
                negative_content += f" :{option['color']}[{option['name']}]"
            st.markdown(negative_content)
            
            # 建置過濾按鈕
            st.pills("推薦度",
                     summary_counter.keys(),
                     selection_mode='single',
                     key='sum_option')
            
            st.pills("正面關鍵字",
                     positive_counter.keys(),
                     selection_mode="multi",
                     key='pos_options')
            
            st.pills("負面關鍵字",
                     negative_counter.keys(),
                     selection_mode="multi",
                     key='neg_options')
            
            st.subheader("整理資料", divider=True)
            
            #* 執行過濾
            final_df = pd.DataFrame(data_list)
            if '推薦度' in final_df.columns and st.session_state.sum_option:
                sum_option = '不推' if st.session_state.sum_option == '不推薦' else st.session_state.sum_option
                sum_condition = [final_df['推薦度'].str.contains(sum_option, na=False)]
                final_df = final_df[reduce(lambda x, y: x & y, sum_condition)]
            
            if '正面關鍵字' in final_df.columns and st.session_state.pos_options:
                pos_condition = [final_df['正面關鍵字'].str.contains(option, na=False) for option in st.session_state.pos_options]
                final_df = final_df[reduce(lambda x, y: x & y, pos_condition)]

            if '負面關鍵字' in final_df.columns and st.session_state.neg_options:
                neg_condition = [final_df['負面關鍵字'].str.contains(option, na=False) for option in st.session_state.neg_options]
                final_df = final_df[reduce(lambda x, y: x & y, neg_condition)]
    
            # 顯示過濾表格
            st.dataframe(final_df, use_container_width=True)

            # === 圓餅圖 ===
            st.subheader("總結", divider=True)
            summary_data = {
                'label': summary_counter.keys(),
                'value': summary_counter.values()
            }
            
            positive_data = {
                'label': positive_counter.keys(),
                'value': positive_counter.values()
            }
            
            negative_data = {
                'label': negative_counter.keys(),
                'value': negative_counter.values()
            }
            
            st.text("總評價比例")
            
            #> 關鍵字計數
            sum_content = ""
            for option in summary_options:
                sum_content += "{}: :{}[{}]\n".format(option['name'],
                                                      option['color'],
                                                      summary_counter[option['name']])
            st.markdown(sum_content)
            
            plt.pie(summary_data['value'], labels=summary_data['label'], autopct='%1.1f%%')
            st.pyplot(plt)
            plt.clf()
            
            st.text("正向關鍵字比例")
            
            #> 關鍵字計數
            pos_content = ""
            for option in positive_options:
                pos_content += "{}: :{}[{}]\n".format(option['name'],
                                                      option['color'],
                                                      positive_counter[option['name']])
            st.markdown(pos_content)
            
            plt.pie(positive_data['value'], labels=positive_data['label'], autopct='%1.1f%%')
            st.pyplot(plt)
            plt.clf()
            
            st.text("負向關鍵字比例")
            
            #> 關鍵字計數
            neg_content = ""
            for option in negative_options:
                neg_content += "{}: :{}[{}]\n".format(option['name'],
                                                      option['color'],
                                                      negative_counter[option['name']])
            st.markdown(neg_content)
            
            plt.pie(negative_data['value'], labels=negative_data['label'], autopct='%1.1f%%')
            st.pyplot(plt)
            plt.clf()
            
            end_parse = time.time()
            
            if st.session_state.analyze_name != st.session_state.hotel_name:
                st.markdown(f"**分析耗時**: :red[{end_analyze - start}] s, **繪製數據圖表耗時**: :red[{end_parse - end_analyze}] s")
            
            analyze_status.update(
                label="評論分析完成", state="complete", expanded=True
            )
            
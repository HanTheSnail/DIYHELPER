# app.py - Main Streamlit Application
import streamlit as st
import pandas as pd
import io

# Page config
st.set_page_config(
    page_title="Bulbshare Link Generator",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    st.title("🔗 Bulbshare Link Generator & Data Matcher")
    st.write("Upload two CSVs to generate Bulbshare links with matched data")
    
    # File uploaders
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("CSV 1 - Main Data")
        st.write("Should contain: Client Name (Col A), Brief Name (Col C), Brief ID (Col ID)")
        csv1 = st.file_uploader("Upload CSV 1", type=['csv'], key="csv1")
    
    with col2:
        st.subheader("CSV 2 - Requirements & Amounts")
        st.write("Should contain: Brief Requirements (Col D), Issued Amount (Col H)")
        csv2 = st.file_uploader("Upload CSV 2", type=['csv'], key="csv2")
    
    if csv1 is not None and csv2 is not None:
        try:
            # Read the CSVs
            df1 = pd.read_csv(csv1)
            df2 = pd.read_csv(csv2)
            
            # Show preview of uploaded data
            with st.expander("📋 Preview CSV 1"):
                st.write(f"Shape: {df1.shape}")
                st.dataframe(df1.head())
                st.write("Columns:", list(df1.columns))
            
            with st.expander("📋 Preview CSV 2"):
                st.write(f"Shape: {df2.shape}")
                st.dataframe(df2.head())
                st.write("Columns:", list(df2.columns))
            
            # Let user select the correct columns if needed
            st.subheader("🔧 Column Mapping")
            
            col1_map, col2_map = st.columns(2)
            
            with col1_map:
                st.write("**CSV 1 Column Selection:**")
                client_col = st.selectbox("Client Name Column", df1.columns, index=0 if len(df1.columns) > 0 else 0)
                brief_name_col = st.selectbox("Brief Name Column", df1.columns, index=2 if len(df1.columns) > 2 else 0)
                brief_id_col = st.selectbox("Brief ID Column", df1.columns, index=len(df1.columns)-1)
            
            with col2_map:
                st.write("**CSV 2 Column Selection:**")
                brief_req_col = st.selectbox("Brief Requirements Column", df2.columns, index=3 if len(df2.columns) > 3 else 0)
                issued_amount_col = st.selectbox("Issued Amount Column", df2.columns, index=7 if len(df2.columns) > 7 else 0)
            
            # Process button
            if st.button("🚀 Generate Links & Match Data", type="primary"):
                
                # Clean the data - remove any whitespace and handle NaN
                df1[brief_name_col] = df1[brief_name_col].astype(str).str.strip()
                df2[brief_req_col] = df2[brief_req_col].astype(str).str.strip()
                
                # Create base URL
                base_url = "https://app.bulbshare.com/2/briefs/create_brief.html?brief="
                
                # Generate Bulbshare links
                df1['Brief_Link'] = df1[brief_id_col].astype(str).apply(
                    lambda x: base_url + x.strip() if pd.notna(x) and x.strip() != '' else ''
                )
                
                # Merge the dataframes on brief name = brief requirements
                merged_df = pd.merge(
                    df1[[client_col, brief_name_col, brief_id_col, 'Brief_Link']], 
                    df2[[brief_req_col, issued_amount_col]], 
                    left_on=brief_name_col, 
                    right_on=brief_req_col, 
                    how='left'
                )
                
                # Create final output dataframe
                result_df = pd.DataFrame({
                    'Client_Name': merged_df[client_col],
                    'Brief_Name': merged_df[brief_name_col],
                    'Brief_Link': merged_df['Brief_Link'],
                    'Issued_Amount': merged_df[issued_amount_col]
                })
                
                # Remove rows where brief link is empty
                result_df = result_df[result_df['Brief_Link'] != '']
                
                # Display results
                st.subheader("✅ Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Matches Found", len(result_df))
                with col2:
                    st.metric("Records from CSV 1", len(df1))
                with col3:
                    st.metric("Records from CSV 2", len(df2))
                
                # Show the final table
                st.dataframe(result_df, use_container_width=True)
                
                # Download button
                csv_buffer = io.StringIO()
                result_df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv_buffer.getvalue(),
                    file_name="bulbshare_links_matched.csv",
                    mime="text/csv"
                )
                
                # Show unmatched records
                unmatched_from_csv1 = df1[~df1[brief_name_col].isin(df2[brief_req_col])]
                unmatched_from_csv2 = df2[~df2[brief_req_col].isin(df1[brief_name_col])]
                
                if len(unmatched_from_csv1) > 0 or len(unmatched_from_csv2) > 0:
                    with st.expander("⚠️ Unmatched Records"):
                        if len(unmatched_from_csv1) > 0:
                            st.write(f"**{len(unmatched_from_csv1)} records from CSV 1 had no match:**")
                            st.dataframe(unmatched_from_csv1[[client_col, brief_name_col]])
                        
                        if len(unmatched_from_csv2) > 0:
                            st.write(f"**{len(unmatched_from_csv2)} records from CSV 2 had no match:**")
                            st.dataframe(unmatched_from_csv2[[brief_req_col, issued_amount_col]])
        
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
            st.write("Please check that your CSV files are formatted correctly.")
    
    else:
        st.info("👆 Please upload both CSV files to get started")
        
        # Show example format
        with st.expander("📋 Expected CSV Format"):
            st.write("**CSV 1 should look like:**")
            example_csv1 = pd.DataFrame({
                'Client_Name': ['Client A', 'Client B', 'Client C'],
                'Column_B': ['Data', 'Data', 'Data'],
                'Brief_Name': ['Project Alpha', 'Project Beta', 'Project Gamma'],
                'Brief_ID': ['brief-67DE3E4D-6D16-11F0-8992-06546FE76FA3', 
                           'brief-89C21275-5E2D-11F0-8992-06546FE76FA3',
                           'brief-12345678-1234-11F0-8992-06546FE76FA3']
            })
            st.dataframe(example_csv1)
            
            st.write("**CSV 2 should look like:**")
            example_csv2 = pd.DataFrame({
                'Col_A': ['Data', 'Data', 'Data'],
                'Col_B': ['Data', 'Data', 'Data'],
                'Col_C': ['Data', 'Data', 'Data'],
                'Brief_Requirements': ['Project Alpha', 'Project Beta', 'Project Delta'],
                'Col_E': ['Data', 'Data', 'Data'],
                'Col_F': ['Data', 'Data', 'Data'],
                'Col_G': ['Data', 'Data', 'Data'],
                'Issued_Amount': [1000, 1500, 2000]
            })
            st.dataframe(example_csv2)

if __name__ == "__main__":
    main()

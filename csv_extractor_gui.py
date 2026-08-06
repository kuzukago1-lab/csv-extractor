from google.colab import files
import io
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, clear_output

print("【CSV行抽出ツール（見出し保持対応版）】")
print("1. 下のボタンから対象のCSVファイルを選択してください。\n")

uploader = widgets.FileUpload(accept='.csv', multiple=False)
display(uploader)

def on_upload_change(change):
    if not uploader.value:
        return
    clear_output(wait=True)
    display(uploader)
    
    try:
        uploaded_file = list(uploader.value.values())[0]
        content = uploaded_file['content']
        
        # 文字コード自動判定
        df = None
        for enc in ['utf-8-sig', 'cp932', 'shift_jis']:
            try:
                df = pd.read_csv(io.BytesIO(content), encoding=enc)
                break
            except Exception:
                continue
                
        if df is None:
            print("\n[エラー] CSVファイルの読み込みに失敗しました。")
            return
            
        print(f"\nファイルを読み込みました！（全データ行数: {len(df)} 行）")
        
        # 入力フォームの表示
        kw_input = widgets.Text(description='検索文字:', placeholder='例: 田中 または 100')
        match_dropdown = widgets.Dropdown(options=[('部分一致', 'partial'), ('完全一致', 'exact')], value='partial', description='一致条件:')
        btn_run = widgets.Button(description='抽出実行', button_style='success')
        out = widgets.Output()
        
        display(widgets.VBox([widgets.HBox([kw_input, match_dropdown]), btn_run, out]))
        
        def on_click(b):
            with out:
                clear_output()
                kw = kw_input.value
                if not kw:
                    print("検索文字を入力してください。")
                    return
                
                m_type = match_dropdown.value
                str_df = df.astype(str)
                if m_type == 'exact':
                    mask = str_df.eq(kw).any(axis=1)
                else:
                    mask = str_df.apply(lambda col: col.str.contains(kw, na=False)).any(axis=1)
                
                result_df = df[mask]
                print(f"--- 抽出結果: 該当 {len(result_df)} 件 （※1行目に見出しが含まれます） ---\n")
                display(result_df.head(20)) # プレビュー
                
                if len(result_df) > 0:
                    out_name = "extracted_result.csv"
                    # index=False で出力しても、Pandasが自動でカラム名（1行目の見出し）を先頭行として保存してくれます
                    result_df.to_csv(out_name, index=False, encoding='utf-8-sig')
                    print(f"\n[保存完了] 見出し付きで '{out_name}' を出力しました。下のリンクからダウンロードできます。")
                    files.download(out_name)
                else:
                    print("\n一致する行はありませんでした。")
                    
        btn_run.on_click(on_click)
        
    except Exception as e:
        print(f"\n[エラー]: {e}")

uploader.observe(on_upload_change, names='value')
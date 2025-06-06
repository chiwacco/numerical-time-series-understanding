import numpy as np
import json
import os
from scipy.signal import find_peaks 

# ピーク値（複数可）を検出し、関連情報と共に新しい辞書として返す関数
def generate_peaks_and_create_dictionary(dataset): 
    """
    データセット内の 'values' からピーク値（複数可）を検出し、
    元のデータセットの情報と合わせて新しい辞書を作成します。
    ピークは scipy.signal.find_peaks を使用して検出されます。
    """
    if 'values' not in dataset or not dataset['values']:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。ピークを検出できません。")
        return {
            **dataset,
            'calculated_peak_values': [], # ピークがない場合は空のリスト
        }

    years = np.array(dataset.get('years_column', [])) # years_column はオプションとして扱う
    values = np.array(dataset['values'], dtype=float) # values は float 型のNumpy配列に

    
    peak_indices, _ = find_peaks(values)
    calculated_peaks = values[peak_indices].tolist()

    result_dictionary = {
        **dataset, # 元のデータセットのキーをすべて保持
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []),
        'values': values.tolist(), # float型に変換されたvaluesリスト
        'calculated_peak_values': calculated_peaks, 
    }
    return result_dictionary

def load_datasets_from_jsonl(file_path):
    """
    JSONLファイルからデータセットのリストを読み込みます。
    1行に1つのJSONオブジェクトが含まれている形式を想定しています。
    """
    datasets = []
    if not os.path.exists(file_path):
        print(f"エラー: ファイル '{file_path}' が見つかりません。")
        return datasets

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, 1):
                try:
                    dataset = json.loads(line)
                    if 'id' not in dataset:
                        dataset['id'] = f"line_{line_number}"
                    datasets.append(dataset)
                except json.JSONDecodeError:
                    print(f"警告: ファイル '{file_path}' の {line_number} 行目が有効なJSONではありません。スキップします: {line.strip()}")
    except IOError as e:
        print(f"エラー: ファイル '{file_path}' の読み込み中にエラーが発生しました: {e}")
        return []
    return datasets

if __name__ == "__main__":
    # ★★★ 入力するJSONLファイル名を指定してください ★★★
    input_jsonl_file = "test.jsonl" 

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)

    if not datasets_from_file:
        print("処理するデータセットがありませんでした。")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件のデータセットを読み込みました。\n")

        processed_results = []
        for i, dataset_doc in enumerate(datasets_from_file):
            print(f"--- データセット {i+1} (ID: {dataset_doc.get('id', 'N/A')}) の処理 ---")
            dictionary_with_peaks = generate_peaks_and_create_dictionary(dataset_doc)
            processed_results.append(dictionary_with_peaks)

            print("検出されたピークが追加された辞書:")
            print(json.dumps(dictionary_with_peaks, indent=4, ensure_ascii=False))
            # ★ 結果のキー名とメッセージを変更
            if dictionary_with_peaks.get('calculated_peak_values'): # リストが空でないかで判定
                print(f"検出されたピーク値のリスト: {dictionary_with_peaks['calculated_peak_values']}")
            elif 'values' in dataset_doc and not dataset_doc['values']:
                 print("ピークは検出されませんでした (valuesが空でした)。")
            elif 'values' not in dataset_doc: # 'values'キーがない場合
                 print("ピークは検出されませんでした (valuesキーがありませんでした)。")
            else: # 'values'はあるがピークがなかった場合
                 print("ピークは検出されませんでした。")
            print("-" * 20)
            print("\n")

        output_jsonl_file = "peaks_output.jsonl" 
        try:
            with open(output_jsonl_file, 'w', encoding='utf-8') as outfile:
                for result_item in processed_results:
                    outfile.write(json.dumps(result_item, ensure_ascii=False) + '\n')
            print(f"処理結果 (ピーク値を含む) を '{output_jsonl_file}' に書き出しました。") # ★ メッセージを変更
        except IOError as e:
            print(f"エラー: 結果のファイル '{output_jsonl_file}'への書き出し中にエラーが発生しました: {e}")

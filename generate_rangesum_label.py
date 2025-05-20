import numpy as np
import json
import os
# import random # np.random を使うので不要です

# 指定範囲内の最大値（RangeMax）を計算し、関連情報と共に新しい辞書として返す関数
def generate_rangemin_and_create_dictionary(dataset): # 関数名を変更
    """
    データセット内の 'values' からランダムに選択された範囲内の最大値を計算し、
    元のデータセットの情報と合わせて新しい辞書を作成します。
    """
    if 'values' not in dataset or not dataset['values']:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' には 'values' キーが存在しないか、空です。範囲内最大値を計算できません。")
        return {
            **dataset,
            'calculated_range_min': None,
            'range_start_index': None,
            'range_end_index': None,
        }

    # years は必須ではないが、元のスクリプトに合わせて処理
    # years_column がなくても values のインデックスで処理可能
    years_list = dataset.get('years_column', [])
    years = np.array(years_list)
    values = np.array(dataset['values'], dtype=float)

    if len(values) < 2: # 範囲を選択するためには少なくとも2つの要素が必要
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' の 'values' の要素が2未満です。範囲内最大値を計算できません。")
        return {
            **dataset,
            'years_column': years_list, # 元のyears_columnをそのまま返す
            'values': values.tolist(),   # floatに変換されたvalues
            'calculated_range_min': None,
            'range_start_index': None,
            'range_end_index': None,
        }

    # start_index と end_index をランダムに生成
    start_index = np.random.randint(0, len(values) - 1)
    # end_index は start_index+1 から len(values)-1 まで
    end_index = np.random.randint(start_index + 1, len(values))

    # 指定した範囲の値を取得
    range_values_slice = values[start_index : end_index + 1] # スライスは end_index を含む
    calculated_range_min_val = np.sum(range_values_slice)

    result_dictionary = {
        **dataset, # 元のデータセットのキーをすべて保持
        'years_column': years.tolist() if years.size > 0 else dataset.get('years_column', []), # 元のキーを上書きする場合
        'values': values.tolist(), # float型に変換されたvaluesリスト (元のキーを上書き)
        'calculated_range_min': calculated_range_min_val, # ★ 計算された範囲内最大値
        'range_start_index': int(start_index),      # ★ ランダムに選ばれた開始インデックス (int型で保存)
        'range_end_index': int(end_index),        # ★ ランダムに選ばれた終了インデックス (int型で保存)
    }
    return result_dictionary

# JSONLファイルからデータセットを読み込む関数 (変更なし)
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
                    if 'id' not in dataset: # IDがなければ行番号ベースで付与
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
            # ★ 関数呼び出しと変数名を変更
            dictionary_with_rangemin = generate_rangemin_and_create_dictionary(dataset_doc)
            processed_results.append(dictionary_with_rangemin)

            print("範囲内最大値が追加された辞書:") # ★ メッセージを変更
            print(json.dumps(dictionary_with_rangemin, indent=4, ensure_ascii=False))
            # ★ 結果のキー名とメッセージを変更
            if dictionary_with_rangemin.get('calculated_range_min') is not None:
                start_idx = dictionary_with_rangemin['range_start_index']
                end_idx = dictionary_with_rangemin['range_end_index']
                print(f"ランダム範囲 [{start_idx}:{end_idx}] の最大値: {dictionary_with_rangemin['calculated_range_min']}")
            elif 'values' in dataset_doc and not dataset_doc['values']:
                 print("範囲内最大値は計算されませんでした (valuesが空でした)。")
            elif 'values' not in dataset_doc or len(dataset_doc.get('values',[])) < 2 : # valuesキーがないか要素数が少ない場合
                 print("範囲内最大値は計算されませんでした (valuesキーがないか、要素数が2未満でした)。")
            print("-" * 20)
            print("\n")

        # 出力ファイル名をここで指定します。必要に応じて変更してください。
        output_jsonl_file = "rangemin_output.jsonl" # ★ 出力ファイル名を変更
        try:
            with open(output_jsonl_file, 'w', encoding='utf-8') as outfile:
                for result_item in processed_results:
                    outfile.write(json.dumps(result_item, ensure_ascii=False) + '\n')
            print(f"処理結果 (範囲内最大値を含む) を '{output_jsonl_file}' に書き出しました。") # ★ メッセージを変更
        except IOError as e:
            print(f"エラー: 結果のファイル '{output_jsonl_file}'への書き出し中にエラーが発生しました: {e}")

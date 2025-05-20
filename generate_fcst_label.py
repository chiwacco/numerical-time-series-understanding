import numpy as np
import json
import os

# 線形回帰で次の値を予測し、関連情報と共に新しい辞書として返す関数
def generate_regression_prediction_and_create_dictionary(dataset): # 関数名を変更
    """
    データセット内の 'values' と 'years_column' を用いて線形回帰を行い、
    次の年の値を予測し、元のデータセットの情報と合わせて新しい辞書を作成します。
    """
    # 'values' と 'years_column' を取得、デフォルトは空リスト
    original_values_list = dataset.get('values', [])
    years_list = dataset.get('years_column', [])

    # 入力データのバリデーションとfloatへの変換を試みる
    try:
        original_values = np.array(original_values_list, dtype=float)
        years = np.array(years_list, dtype=float)
    except ValueError:
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}' の 'values' または 'years_column' に数値に変換できない要素が含まれています。")
        return {
            **dataset,
            'calculated_next_value_regression': None,
            'next_year_for_prediction': None,
            'regression_error': 'Invalid data type in values or years_column.',
        }

    if len(original_values) < 2 or len(years) < 2 or len(original_values) != len(years):
        error_msg = 'Not enough data points for linear regression (requires at least 2 points with corresponding years) or mismatched lengths.'
        print(f"警告: データセットID '{dataset.get('id', 'N/A')}': {error_msg}")
        return {
            **dataset,
            'original_values_for_regression': original_values.tolist(), # エラー時も入力値を保持
            'years_for_regression': years.tolist(),                # エラー時も入力値を保持
            'calculated_next_value_regression': None,
            'next_year_for_prediction': None,
            'regression_error': error_msg,
        }

    try:
        slope, intercept = np.polyfit(years, original_values, 1)
    except Exception as e:
        error_msg = f'Failed to fit linear regression model: {e}'
        print(f"エラー: データセットID '{dataset.get('id', 'N/A')}': {error_msg}")
        return {
            **dataset,
            'original_values_for_regression': original_values.tolist(),
            'years_for_regression': years.tolist(),
            'calculated_next_value_regression': None,
            'next_year_for_prediction': None,
            'regression_error': error_msg,
        }

    # 次の年を予測 (現在の年の最大値 + 1)
    next_year_to_predict_val = np.max(years) + 1 if len(years) > 0 else None
    # 次の年の値を予測
    calculated_next_val = (slope * next_year_to_predict_val + intercept) if next_year_to_predict_val is not None else None

    result_dictionary = {
        **dataset, # 元のデータセットのキーをすべて保持
        'original_values_for_regression': original_values.tolist(), # 回帰に使用した元の値
        'years_for_regression': years.tolist(),                # 回帰に使用した元の年
        'calculated_next_value_regression': float(calculated_next_val) if calculated_next_val is not None else None, # ★ 計算された次の値
        'next_year_for_prediction': float(next_year_to_predict_val) if next_year_to_predict_val is not None else None, # ★ 予測対象の次の年
        'regression_slope': float(slope), # 参考情報として傾き
        'regression_intercept': float(intercept) # 参考情報として切片
    }
    return result_dictionary

def load_datasets_from_jsonl(file_path):
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
    input_jsonl_file = "test.jsonl" 

    datasets_from_file = load_datasets_from_jsonl(input_jsonl_file)

    if not datasets_from_file:
        print("処理するデータセットがありませんでした。")
    else:
        print(f"'{input_jsonl_file}' から {len(datasets_from_file)} 件のデータセットを読み込みました。\n")

        processed_results = []
        for i, dataset_doc in enumerate(datasets_from_file):
            print(f"--- データセット {i+1} (ID: {dataset_doc.get('id', 'N/A')}) の処理 ---")
            dictionary_with_regression = generate_regression_prediction_and_create_dictionary(dataset_doc)
            processed_results.append(dictionary_with_regression)

            print("線形回帰による次値予測が追加された辞書:") 
            print(json.dumps(dictionary_with_regression, indent=4, ensure_ascii=False))
            if dictionary_with_regression.get('regression_error'):
                print(f"エラー: {dictionary_with_regression['regression_error']}")
            elif dictionary_with_regression.get('calculated_next_value_regression') is not None:
                next_year = dictionary_with_regression['next_year_for_prediction']
                next_val = dictionary_with_regression['calculated_next_value_regression']
                print(f"予測対象の次の年: {next_year}, 予測された次の値: {next_val:.2f}") 
            else:
                print("次値予測は実行されませんでした。")
            print("-" * 20)
            print("\n")

        output_jsonl_file = "regression_prediction_output.jsonl"
        try:
            with open(output_jsonl_file, 'w', encoding='utf-8') as outfile:
                for result_item in processed_results:
                    outfile.write(json.dumps(result_item, ensure_ascii=False) + '\n')
            print(f"処理結果 (線形回帰予測を含む) を '{output_jsonl_file}' に書き出しました。") 
        except IOError as e:
            print(f"エラー: 結果のファイル '{output_jsonl_file}'への書き出し中にエラーが発生しました: {e}")

# WSUS Server Core Role - Test Guide

このディレクトリには、Azure 上にテスト用の Windows Server インスタンスを構築し、WSUS Role の Pester テストを実行するための環境が含まれています。

## 📋 前提条件

*   Terraform installed
*   Ansible installed
*   Azure CLI (`az login` でログイン済みであること)

## 📁 ディレクトリ構成

*   `azure_infra/`: Terraform コード。Azure 上に VM とネットワークリソースを作成します。
*   `pester/`: Pester テストコード (`Wsus.Tests.ps1`)。
*   `inventory.ini`: テスト対象のインベントリファイル。
*   `test_pester.yml`: Pester テストを実行するための Playbook。

## 🚀 テスト環境の構築 (Terraform)

1.  `azure_infra` ディレクトリに移動します。
    ```bash
    cd azure_infra
    ```

2.  Terraform を初期化します。
    ```bash
    terraform init
    ```

3.  `terraform.tfvars` ファイルを作成・編集し、`admin_password` を設定します（必要な場合）。
    ```hcl
    admin_password = "YourStrongPassword123!"
    ```

4.  リソースを作成します。
    ```bash
    terraform apply
    ```
    *   確認プロンプトで `yes` を入力します。

5.  出力された Public IP アドレスをメモします。
    ```bash
    # 出力例
    public_ip_address = "20.10.10.10"
    ```

## 📝 インベントリの設定

`tests/inventory.ini` を編集し、Terraform で取得した IP アドレスと、設定したパスワードを反映させます。

```ini
[wsus_servers]
<Public_IP_Address>

[wsus_servers:vars]
ansible_user=azureuser
ansible_password="YourStrongPassword123!"
ansible_connection=winrm
ansible_winrm_server_cert_validation=ignore
ansible_winrm_transport=ntlm
```

## 🧪 テストの実行

Project root または `tests` ディレクトリから以下のコマンドを実行し、Pester テストを実行します。

```bash
access ansible-playbook -i inventory.ini test_pester.yml
```

この Playbook は以下の処理を行います：
1.  Pester モジュールのインストール
2.  テストファイル (`Wsus.Tests.ps1`) の転送
3.  テストの実行と結果の表示

## 🧹 環境の削除

テストが完了したら、Azure リソースを削除して課金を停止します。

```bash
cd azure_infra
terraform destroy
```
*   確認プロンプトで `yes` を入力します。

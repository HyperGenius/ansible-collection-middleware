resource "azurerm_windows_virtual_machine" "vm" {
  name                = "${var.prefix}-vm"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  size                = "Standard_B2as_v2"

  # Spotインスタンス設定を追加
  priority        = "Spot"
  eviction_policy = "Delete"
  max_bid_price   = -1 # -1 は「価格による停止はしない（容量不足のみ停止）」の意味

  admin_username = var.admin_username
  admin_password = var.admin_password
  network_interface_ids = [
    azurerm_network_interface.nic.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2025-datacenter-smalldisk-g2"
    version   = "latest"
  }

}

# WinRM設定スクリプトの自動実行
resource "azurerm_virtual_machine_extension" "winrm_setup" {
  name                 = "winrm-setup"
  virtual_machine_id   = azurerm_windows_virtual_machine.vm.id
  publisher            = "Microsoft.Compute"
  type                 = "CustomScriptExtension"
  type_handler_version = "1.10"

  settings = <<SETTINGS
    {
        "fileUris": ["https://raw.githubusercontent.com/ansible/ansible-documentation/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"],
        "commandToExecute": "powershell.exe -ExecutionPolicy Unrestricted -File ConfigureRemotingForAnsible.ps1"
    }
SETTINGS

  # VM作成後に実行されるように依存関係を明示（ID参照してるので暗黙的にも効きますが念の為）
  depends_on = [azurerm_windows_virtual_machine.vm]
}

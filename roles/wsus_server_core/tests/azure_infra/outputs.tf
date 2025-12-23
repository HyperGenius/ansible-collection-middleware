output "public_ip" {
  description = "VMのパブリックIPアドレス"
  value       = azurerm_public_ip.pip.ip_address
}

output "username" {
  description = "管理者ユーザー名"
  value       = var.admin_username
}

output "password" {
  description = "管理者パスワード"
  value       = var.admin_password
  sensitive   = true
}

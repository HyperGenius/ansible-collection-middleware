variable "prefix" {
  description = "リソース名のプレフィックス"
  default     = "ansible-test"
}

variable "location" {
  description = "リソースを作成するリージョン"
  default     = "Japan East"
}

variable "admin_username" {
  description = "VMの管理者ユーザー名"
  default     = "azureuser"
}

variable "admin_password" {
  description = "VMの管理者パスワード"
  sensitive   = true
}

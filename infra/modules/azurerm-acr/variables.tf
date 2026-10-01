variable "acrs" {
  type = map(object({
    acr_name      = string
    sku           = string
    admin_enabled = bool
    rg_name       = string
    location      = string
    tags          = map(string)
  }))
}

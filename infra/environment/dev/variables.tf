variable "subscription_id" {
  description = "The subscription ID"
  type        = string
}

variable "resource_groups" {
  type = map(object({
    name     = string
    location = string
    tags     = map(string)
  }))
}

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

variable "aks_clusters" {
  type = map(object({
    aks_name   = string
    location   = string
    dns_prefix = string
    rg_name    = string

    default_node_pool = object({
      name                = string
      node_count          = number
      vm_size             = string
      enable_auto_scaling = bool
      min_count           = number
      max_count           = number
    })

    identity = object({
      type = string
    })

    network_profile = object({
      network_plugin      = string
      network_plugin_mode = string
      network_policy      = string
      load_balancer_sku   = string
    })

    tags = map(string)
  }))
}


variable "role_assignment" {
  type = map(object({
   # spn_key = string
    aks_key = string
    acr_key = string
  }))
}

# variable "spn_object_id" {
#   type = string
# }

# variable "acr_ids" {
#   type = map(string)
# }

# variable "aks_ids" {
#   type = map(string)
# }

# variable "kubelet_ids" {
#   type = map(string)
# }

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

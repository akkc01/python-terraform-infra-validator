resource "azurerm_kubernetes_cluster" "aks" {
  for_each            = var.aks_clusters
  name                = each.value.aks_name
  location            = each.value.location
  resource_group_name = each.value.rg_name
  dns_prefix          = each.value.dns_prefix

  default_node_pool {
    name                = each.value.default_node_pool.name
    node_count          = each.value.default_node_pool.node_count
    vm_size             = each.value.default_node_pool.vm_size
    enable_auto_scaling = each.value.default_node_pool.enable_auto_scaling
    min_count           = each.value.default_node_pool.min_count
    max_count           = each.value.default_node_pool.max_count
  }

  identity {
    type = each.value.identity.type
  }

  network_profile {
    network_plugin      = each.value.network_profile.network_plugin
    load_balancer_sku   = each.value.network_profile.load_balancer_sku
    network_plugin_mode = each.value.network_profile.network_plugin_mode
    network_policy      = each.value.network_profile.network_policy
  }

  tags = each.value.tags
}





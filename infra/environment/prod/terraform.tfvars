resource_groups = {
  aks-rg = {
    name     = "axion-app-aks-rg"
    location = "koreacentral"
    tags = {
      env     = "dev"
      team    = "jarvis"
      project = "axion"
    }
  }
}

acrs = {
  acr1 = {
    acr_name      = "axionappacrakkc01"
    sku           = "Standard"
    admin_enabled = false
    rg_name       = "axion-app-aks-rg"
    location      = "koreacentral"
    tags = {
      env     = "dev"
      team    = "jarvis"
      project = "axion"
    }
  }
}

aks_clusters = {
  aks1 = {
    aks_name   = "axion-app-aks"
    dns_prefix = "devaksdns"
    rg_name    = "axion-app-aks-rg"
    location   = "koreacentral"

    default_node_pool = {
      name                = "default"
      node_count          = 1
      vm_size             = "Standard_D4as_v5"
      enable_auto_scaling = true
      min_count           = 1
      max_count           = 1
    }
    identity = {
      type = "SystemAssigned"
    }
    network_profile = {
      network_plugin      = "azure"
      network_plugin_mode = "overlay"
      network_policy      = "calico"
      load_balancer_sku   = "standard"
    }

    tags = {
      env     = "dev"
      team    = "jarvis"
      project = "axion"
    }
  }
}

role_assignment = {
  dev = {
 #   spn_key = "spn1"
    aks_key = "aks1"
    acr_key = "acr1"
  }
}

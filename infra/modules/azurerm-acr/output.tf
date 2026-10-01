output "acr_ids" {
  description = "Map of ACR names to ACR resource IDs"
  value = {
    for key, acr in azurerm_container_registry.acr :
    key => acr.id
  }
}


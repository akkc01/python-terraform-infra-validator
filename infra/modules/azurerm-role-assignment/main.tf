# Role Assignment for AKS to pull image from ACR
resource "azurerm_role_assignment" "acr_pull" {
  for_each             = var.role_assignment
  principal_id         = var.kubelet_ids[each.value.aks_key]
  role_definition_name = "AcrPull"
  scope                = var.acr_ids[each.value.acr_key]
}

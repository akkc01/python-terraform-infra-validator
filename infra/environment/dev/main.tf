module "rgs" {
  source          = "../../modules/azurerm-resource-group"
  resource_groups = var.resource_groups

}

module "acrs" {
  depends_on = [module.rgs]
  source     = "../../modules/azurerm-acr"
  acrs       = var.acrs
}

# module "aks" {
#   depends_on   = [module.rgs]
#   source       = "../../modules/azurerm-aks"
#   aks_clusters = var.aks_clusters
# }

# module "role_assignment" {
#   depends_on = [ module.rgs, module.acrs, module.aks,module.spn ]
#   source = "../../modules/azurerm-role-assignment"
#   role_assignment = var.role_assignment
#  # spn_object_ids = module.spn.spn_object_ids
#   acr_ids       = module.acrs.acr_ids
#  # aks_ids       = module.aks.aks_ids
#   kubelet_ids   = module.aks.kubelet_identity_object_ids
# }


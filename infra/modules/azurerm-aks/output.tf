output "aks_ids" {
  description = "AKS resource IDs"
  value = {
    for key, aks in azurerm_kubernetes_cluster.aks :
    key => aks.id
  }
}


output "kubelet_identity_object_ids" {
  value = {
    for key, aks in azurerm_kubernetes_cluster.aks :
    key => aks.kubelet_identity[0].object_id
  }
}
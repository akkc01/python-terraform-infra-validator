import os
import sys
import subprocess
import time
from typing import Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.authorization import AuthorizationManagementClient


# ============================================================
# Configuration
# ============================================================

SUBSCRIPTION_ID = os.environ["AZURE_SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["AKS_RESOURCE_GROUP"]
AKS_NAME = os.environ["AKS_NAME"]
ACR_NAME = os.environ["ACR_NAME"]

TEST_IMAGE = os.getenv(
    "TEST_IMAGE",
    "mcr.microsoft.com/azuredocs/aci-helloworld:latest"
)

TEST_NAMESPACE = os.getenv(
    "TEST_NAMESPACE",
    "infra-validation"
)

TEST_POD_NAME = os.getenv(
    "TEST_POD_NAME",
    "acr-pull-test"
)


# ============================================================
# Azure Authentication
# ============================================================

def get_credential():

    print("Authenticating with Azure...")

    credential = DefaultAzureCredential()

    print("Azure authentication successful.")

    return credential


# ============================================================
# Azure Clients
# ============================================================

def create_clients(credential):

    acr_client = ContainerRegistryManagementClient(
        credential,
        SUBSCRIPTION_ID
    )

    aks_client = ContainerServiceClient(
        credential,
        SUBSCRIPTION_ID
    )

    authorization_client = AuthorizationManagementClient(
        credential,
        SUBSCRIPTION_ID
    )

    return acr_client, aks_client, authorization_client


# ============================================================
# Check ACR
# ============================================================

def validate_acr(acr_client) -> Optional[object]:

    print("\n====================================")
    print("1. Validating Azure Container Registry")
    print("====================================")

    try:
        acr = acr_client.registries.get(
            RESOURCE_GROUP,
            ACR_NAME
        )
        print(f"ACR Name       : {acr.name}")
        print(f"Login Server   : {acr.login_server}")
        print(f"Location       : {acr.location}")
        print(f"SKU            : {acr.sku.name}")
        print("ACR Status     : PASS")
        return acr

    except Exception as exc:
        print("ACR Status     : FAIL")
        print(f"Error          : {exc}")
        return None


# ============================================================
# Check AKS
# ============================================================

def validate_aks(aks_client) -> Optional[object]:
    print("\n====================================")
    print("2. Validating AKS Cluster")
    print("====================================")

    try:
        aks = aks_client.managed_clusters.get(
            RESOURCE_GROUP,
            AKS_NAME
        )
        print(f"AKS Name       : {aks.name}")
        print(f"Location       : {aks.location}")
        print(f"Provisioning   : {aks.provisioning_state}")

        if aks.provisioning_state != "Succeeded":
            print("AKS Status     : FAIL")
            print(
                f"Expected provisioning state "
                f"'Succeeded', got '{aks.provisioning_state}'"
            )
            return None
        print("AKS Status     : PASS")
        return aks

    except Exception as exc:
        print("AKS Status     : FAIL")
        print(f"Error          : {exc}")
        return None


# ============================================================
# Check AcrPull Role Assignment
# ============================================================

def validate_acr_pull(
    authorization_client,
    aks
):

    print("\n====================================")
    print("3. Validating AcrPull Permission")
    print("====================================")

    try:
        identity = aks.identity
        if identity is None:
            print("Managed Identity : FAIL")
            print("AKS does not have a managed identity.")
            return False

        principal_id = identity.principal_id
        print(f"AKS Principal ID : {principal_id}")
        role_assignments = (
            authorization_client.role_assignments.list_for_scope(
                f"/subscriptions/{SUBSCRIPTION_ID}"
            )
        )

        acr_scope = (
            f"/subscriptions/{SUBSCRIPTION_ID}"
            f"/resourceGroups/{RESOURCE_GROUP}"
            f"/providers/Microsoft.ContainerRegistry"
            f"/registries/{ACR_NAME}"
        )
        acr_pull_found = False
        for assignment in role_assignments:
            if not assignment.principal_id:
                continue
            if assignment.principal_id.lower() != principal_id.lower():
                continue
            if not assignment.scope:
                continue
            if assignment.scope.lower() != acr_scope.lower():
                continue
            role_definition_id = (
                assignment.role_definition_id or ""
            )
            if "7f951dda-4ed3-4680-a7ca-43fe172d538d" in \
                    role_definition_id.lower():
                acr_pull_found = True
                print("AcrPull Role     : FOUND")
                print("AcrPull Status   : PASS")
                return True
        print("AcrPull Role     : NOT FOUND")
        print("AcrPull Status   : FAIL")
        return False

    except Exception as exc:
        print("AcrPull Status   : FAIL")
        print(f"Error            : {exc}")
        return False


# ============================================================
# Get AKS Credentials
# ============================================================

def get_aks_credentials():

    print("\n====================================")
    print("4. Getting AKS Credentials")
    print("====================================")

    command = [
        "az",
        "aks",
        "get-credentials",
        "--resource-group",
        RESOURCE_GROUP,
        "--name",
        AKS_NAME,
        "--admin",
        "--overwrite-existing"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print("AKS Credentials : FAIL")
        print(result.stderr)

        return False

    print("AKS Credentials : PASS")

    return True


# # ============================================================
# # Create Test Namespace
# # ============================================================

# def create_namespace():

#     print("\n====================================")
#     print("5. Creating Validation Namespace")
#     print("====================================")

#     command = [
#         "kubectl",
#         "create",
#         "namespace",
#         TEST_NAMESPACE
#     ]

#     result = subprocess.run(
#         command,
#         capture_output=True,
#         text=True
#     )

#     if result.returncode != 0:

#         # Namespace might already exist.
#         if "AlreadyExists" in result.stderr:

#             print(
#                 f"Namespace '{TEST_NAMESPACE}' "
#                 "already exists."
#             )

#             return True

#         print("Namespace creation : FAIL")
#         print(result.stderr)

#         return False

#     print("Namespace creation : PASS")

#     return True


# # ============================================================
# # Test Image Pull
# # ============================================================

# def create_test_pod():

#     print("\n====================================")
#     print("6. Testing ACR/Image Pull")
#     print("====================================")

#     pod_yaml = f"""
# apiVersion: v1
# kind: Pod
# metadata:
#   name: {TEST_POD_NAME}
#   namespace: {TEST_NAMESPACE}
# spec:
#   restartPolicy: Never
#   containers:
#   - name: test
#     image: {TEST_IMAGE}
#     command:
#     - /bin/sh
#     - -c
#     - "echo ACR_IMAGE_PULL_SUCCESS; sleep 10"
# """

#     process = subprocess.run(
#         [
#             "kubectl",
#             "apply",
#             "-f",
#             "-"
#         ],
#         input=pod_yaml,
#         text=True,
#         capture_output=True
#     )

#     if process.returncode != 0:

#         print("Test Pod creation : FAIL")
#         print(process.stderr)

#         return False

#     print("Test Pod created.")

#     return True


# # ============================================================
# # Wait for Pod
# # ============================================================

# def wait_for_pod():

#     print("\n====================================")
#     print("7. Waiting for Image Pull")
#     print("====================================")

#     timeout = 180
#     interval = 10
#     elapsed = 0

#     while elapsed < timeout:

#         result = subprocess.run(
#             [
#                 "kubectl",
#                 "get",
#                 "pod",
#                 TEST_POD_NAME,
#                 "-n",
#                 TEST_NAMESPACE,
#                 "-o",
#                 "jsonpath={.status.phase}"
#             ],
#             capture_output=True,
#             text=True
#         )

#         phase = result.stdout.strip()

#         print(
#             f"Pod Status after "
#             f"{elapsed}s: {phase}"
#         )

#         if phase == "Succeeded":

#             print("\nImage Pull Test : PASS")

#             return True

#         if phase == "Failed":

#             print("\nImage Pull Test : FAIL")

#             return False

#         # Check container waiting reason.
#         describe = subprocess.run(
#             [
#                 "kubectl",
#                 "describe",
#                 "pod",
#                 TEST_POD_NAME,
#                 "-n",
#                 TEST_NAMESPACE
#             ],
#             capture_output=True,
#             text=True
#         )

#         output = describe.stdout

#         if "ImagePullBackOff" in output:

#             print(
#                 "ImagePullBackOff detected."
#             )

#             print(output)

#             return False

#         if "ErrImagePull" in output:

#             print(
#                 "ErrImagePull detected."
#             )

#             print(output)

#             return False

#         time.sleep(interval)

#         elapsed += interval

#     print(
#         "\nImage Pull Test : TIMEOUT"
#     )

#     return False


# # ============================================================
# # Cleanup
# # ============================================================

# def cleanup():

#     print("\n====================================")
#     print("8. Cleaning Test Resources")
#     print("====================================")

#     subprocess.run(
#         [
#             "kubectl",
#             "delete",
#             "pod",
#             TEST_POD_NAME,
#             "-n",
#             TEST_NAMESPACE,
#             "--ignore-not-found=true"
#         ],
#         capture_output=True,
#         text=True
#     )

#     subprocess.run(
#         [
#             "kubectl",
#             "delete",
#             "namespace",
#             TEST_NAMESPACE,
#             "--ignore-not-found=true"
#         ],
#         capture_output=True,
#         text=True
#     )

#     print("Cleanup completed.")


# # ============================================================
# # Main
# # ============================================================

# def main():

#     print("\n")
#     print("============================================")
#     print(" AKS + ACR Infrastructure Validation")
#     print("============================================")

#     validation_failed = False

#     try:

#         credential = get_credential()

#         (
#             acr_client,
#             aks_client,
#             authorization_client
#         ) = create_clients(credential)

#         # ----------------------------------------
#         # ACR
#         # ----------------------------------------

#         acr = validate_acr(acr_client)

#         if acr is None:

#             validation_failed = True

#         # ----------------------------------------
#         # AKS
#         # ----------------------------------------

#         aks = validate_aks(aks_client)

#         if aks is None:

#             validation_failed = True

#         # ----------------------------------------
#         # AcrPull
#         # ----------------------------------------

#         if aks is not None:

#             acr_pull_ok = validate_acr_pull(
#                 authorization_client,
#                 aks
#             )

#             if not acr_pull_ok:

#                 validation_failed = True

#         # ----------------------------------------
#         # Kubernetes validation
#         # ----------------------------------------

#         if not validation_failed:

#             credentials_ok = get_aks_credentials()

#             if not credentials_ok:

#                 validation_failed = True

#         if not validation_failed:

#             namespace_ok = create_namespace()

#             if not namespace_ok:

#                 validation_failed = True

#         if not validation_failed:

#             pod_ok = create_test_pod()

#             if not pod_ok:

#                 validation_failed = True

#         if not validation_failed:

#             image_pull_ok = wait_for_pod()

#             if not image_pull_ok:

#                 validation_failed = True

#     finally:

#         cleanup()

#     # --------------------------------------------
#     # Final result
#     # --------------------------------------------

#     print("\n")
#     print("============================================")
#     print(" Final Infrastructure Validation Result")
#     print("============================================")

#     if validation_failed:

#         print("RESULT: FAILED")

#         sys.exit(1)

#     print("RESULT: PASSED")

#     sys.exit(0)


# if __name__ == "__main__":
#     main()
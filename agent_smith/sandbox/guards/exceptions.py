
class SandboxSecurityViolation(Exception):
    ...


class ModuleNotAuthorizedError(SandboxSecurityViolation):
    ...


class FilesystemRestrictedError(SandboxSecurityViolation):
    ...


class NetworkAccessNotAuthorizedError(SandboxSecurityViolation):
    ...


class ExceedingMemorySizeError(SandboxSecurityViolation):
    ...

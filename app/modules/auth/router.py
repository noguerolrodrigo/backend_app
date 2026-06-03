from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import create_access_token
from app.core.deps import get_current_user, require_role
from app.modules.usuario.service import UsuarioService, RolService, UsuarioRolService
from app.modules.usuario.models import Usuario
from app.modules.usuario.usuario_uow import UsuarioUnitOfWork
from app.modules.auth.schemas import LoginRequest, RegisterRequest, LoginResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """Authenticate user and return JWT token with roles"""
    with UsuarioUnitOfWork() as uow:
        service = UsuarioService(uow)
        user = service.verificar_contrasena(data.email, data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )

        role_codes = [rol.codigo for rol in user.roles]
        access_token = create_access_token({
            "user_id": user.id,
            "email": user.email,
            "roles": role_codes
        })

    return LoginResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email,
        nombre=user.nombre,
        apellido=user.apellido,
        roles=role_codes
    )


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    """Register a new user with CLIENT role and return JWT

    This endpoint is PUBLIC (no auth required). Creates a user and
    automatically assigns the CLIENT role.
    """
    from app.modules.usuario.schemas import UsuarioCreate

    try:
        with UsuarioUnitOfWork() as uow:
            # 1. Crear usuario via UsuarioService
            usuario_service = UsuarioService(uow)
            usuario_create = UsuarioCreate(
                email=data.email,
                nombre=data.nombre,
                apellido=data.apellido,
                password=data.password,
                activo=True
            )
            usuario = usuario_service.crear_usuario(usuario_create)

            # 2. Buscar rol CLIENT y asignarlo
            rol_service = RolService(uow)
            usuario_rol_service = UsuarioRolService(uow)
            rol_client = rol_service.obtener_rol_por_codigo("CLIENT")
            if rol_client:
                try:
                    usuario_rol_service.asignar_rol_a_usuario(usuario.id, rol_client.id)
                except ValueError:
                    pass  # Ya tiene el rol (no debería pasar en creación)

            # 3. Recargar con roles
            uow.session.refresh(usuario)
            role_codes = [rol.codigo for rol in usuario.roles]

            # 4. Generar JWT
            access_token = create_access_token({
                "user_id": usuario.id,
                "email": usuario.email,
                "roles": role_codes
            })

            # commit automático al salir del with

        return LoginResponse(
            access_token=access_token,
            user_id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            roles=role_codes
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=LoginResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    """Get current user info from token"""
    role_codes = [rol.codigo for rol in current_user.roles]
    # Return empty token since we don't need to re-issue
    return LoginResponse(
        access_token="",
        user_id=current_user.id,
        email=current_user.email,
        nombre=current_user.nombre,
        apellido=current_user.apellido,
        roles=role_codes
    )


@router.get("/verify")
def verify_token(current_user: Usuario = Depends(get_current_user)):
    """Verify the current token is valid"""
    role_codes = [rol.codigo for rol in current_user.roles]
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "roles": role_codes
    }

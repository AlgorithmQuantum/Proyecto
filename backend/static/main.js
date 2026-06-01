// ── Funciones generales ──────────────────────────────────────────

function cerrarSesion() { window.location.href = 'auth/logout'; }
function inicioSesion()  { window.location.href = "auth/login"; }
function crearCuenta()   { window.location.href = "auth/registro"; }
function inicio()        { window.location.href = "/"; }
function doctores()      { window.location.href = "/doctores"; }
function privacidad()    { window.location.href = "/privacidad"; }
function especialidades(){ window.location.href = "/especialidades"; }


// ── Login page ───────────────────────────────────────────────────

function mostrarMensaje(tipo, mensaje) {
    const mensajesDiv = document.getElementById('mensajes');
    if (!mensajesDiv) return;
    const icono = tipo === 'error' ? 'exclamation' : 'check';
    const clase = tipo === 'error' ? 'mensaje-error' : 'mensaje-exito';
    mensajesDiv.innerHTML = `
        <div class="${clase}">
            <i class="fa-solid fa-circle-${icono}"></i> ${mensaje}
        </div>`;
    setTimeout(() => { mensajesDiv.innerHTML = ''; }, 5000);
}

function validarCampo(input, helpId, reglas) {
    const helpEl = document.getElementById(helpId);
    const valor  = input.value.trim();
    const fallo  = reglas.find(r => !r.test(valor));

    if (fallo) {
        input.classList.add('campo-invalido');
        input.classList.remove('campo-valido');
        helpEl.textContent = '❌ ' + fallo.msg;
        helpEl.style.color = '#dc3545';
        return false;
    }
    input.classList.remove('campo-invalido');
    input.classList.add('campo-valido');
    helpEl.textContent = '✓ Válido';
    helpEl.style.color = '#28a745';
    return true;
}

function setupTogglePassword() {
    const campo  = document.getElementById('campoPassword');
    const boton  = document.getElementById('btnAlternarPassword');
    if (!campo || !boton) return;

    boton.addEventListener('click', () => {
        const esPassword = campo.type === 'password';
        campo.type = esPassword ? 'text' : 'password';
        boton.classList.toggle('fa-eye',       !esPassword);
        boton.classList.toggle('fa-eye-slash',  esPassword);
    });
}

function setupValidaciones() {
    const usuarioInput  = document.getElementById('usuario');
    const passwordInput = document.getElementById('campoPassword');
    const loginForm     = document.getElementById('loginForm');
    const btnIngresar   = document.getElementById('btnIngresar');
    if (!loginForm) return;

    const reglasUsuario = [
        { test: v => v !== '',   msg: 'El usuario o correo es obligatorio' },
        { test: v => v.length >= 3, msg: 'Debe tener al menos 3 caracteres' },
    ];
    const reglasPassword = [
        { test: v => v !== '',   msg: 'La contraseña es obligatoria' },
        { test: v => v.length >= 6, msg: 'Debe tener al menos 6 caracteres' },
    ];

    const validarUsuario  = () => validarCampo(usuarioInput,  'usuarioHelp',  reglasUsuario);
    const validarPassword = () => validarCampo(passwordInput, 'passwordHelp', reglasPassword);

    usuarioInput.addEventListener('input', validarUsuario);
    usuarioInput.addEventListener('blur',  validarUsuario);
    passwordInput.addEventListener('input', validarPassword);
    passwordInput.addEventListener('blur',  validarPassword);

    loginForm.addEventListener('submit', (e) => {
        const ok = validarUsuario() & validarPassword(); // ambos siempre se evalúan
        if (!ok) {
            e.preventDefault();
            mostrarMensaje('error', 'Por favor corrige los errores antes de continuar');
            document.querySelector('.campo-invalido')
                    ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            btnIngresar.disabled = true;
            btnIngresar.innerHTML = 'Verificando credenciales... <i class="fa-solid fa-spinner fa-spin"></i>';
        }
    });
}

function initLogin() {
    const data = document.getElementById('loginData')?.dataset;
    if (!data) return;

    setupTogglePassword();
    setupValidaciones();

    // Mensajes provenientes del servidor (Flask)
    if (data.error)   mostrarMensaje('error', data.error);
    if (data.success) mostrarMensaje('exito', data.success);
}

// Solo se activa si existe el elemento ancla del login
if (document.getElementById('loginData')) {
    document.addEventListener('DOMContentLoaded', initLogin);
}
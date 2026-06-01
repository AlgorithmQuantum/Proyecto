// ── Funciones generales ──────────────────────────────────────────────────────

function cerrarSesion()   { window.location.href = 'auth/logout'; }
function inicioSesion()   { window.location.href = "auth/login"; }
function crearCuenta()    { window.location.href = "auth/registro"; }
function inicio()         { window.location.href = "/"; }
function doctores()       { window.location.href = "/doctores"; }
function privacidad()     { window.location.href = "/privacidad"; }
function especialidades() { window.location.href = "/especialidades"; }


// ── Utilidades de validación ──────────────────────────────────────────────────

/**
 * Marca un campo como válido o inválido y muestra el mensaje de ayuda.
 * @param {HTMLElement} input   - El campo a validar
 * @param {string}      helpId  - id del <span> de ayuda
 * @param {boolean}     esValido
 * @param {string}      mensajeError
 */
function marcarCampo(input, helpId, esValido, mensajeError = '') {
    const helpEl = document.getElementById(helpId);
    if (!helpEl) return;

    if (esValido) {
        input.classList.remove('campo-invalido');
        input.classList.add('campo-valido');
        helpEl.textContent = '✓ Válido';
        helpEl.style.color = '#28a745';
    } else {
        input.classList.remove('campo-valido');
        input.classList.add('campo-invalido');
        helpEl.textContent = '❌ ' + mensajeError;
        helpEl.style.color = '#dc3545';
    }
}

/** Limpia el estado de validación de un campo */
function limpiarCampo(input, helpId, textoOriginal = '') {
    input.classList.remove('campo-valido', 'campo-invalido');
    const helpEl = document.getElementById(helpId);
    if (helpEl) {
        helpEl.textContent = textoOriginal;
        helpEl.style.color = '';
    }
}

/** Muestra un mensaje global de éxito o error en el div #mensajes */
function mostrarMensaje(tipo, mensaje) {
    const mensajesDiv = document.getElementById('mensajes');
    if (!mensajesDiv) return;
    const icono = tipo === 'error' ? 'exclamation' : 'check';
    const clase = tipo === 'error' ? 'mensaje-error' : 'mensaje-exito';
    mensajesDiv.innerHTML = `
        <div class="${clase}">
            <i class="fa-solid fa-circle-${icono}"></i> ${mensaje}
        </div>`;
    setTimeout(() => { mensajesDiv.innerHTML = ''; }, 6000);
}


// ── Reglas de validación individuales ────────────────────────────────────────

const REGEX_CURP = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z\d]\d$/;
const REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const REGEX_SOLO_LETRAS = /^[a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s'-]+$/;

function validarNombre(input, helpId) {
    const v = input.value.trim();
    if (!v)                        return marcarCampo(input, helpId, false, 'El nombre es obligatorio'),          false;
    if (v.length < 2)              return marcarCampo(input, helpId, false, 'Mínimo 2 caracteres'),              false;
    if (!REGEX_SOLO_LETRAS.test(v)) return marcarCampo(input, helpId, false, 'Solo se permiten letras'),         false;
    marcarCampo(input, helpId, true);
    return true;
}

function validarApellido(input, helpId, etiqueta = 'El apellido') {
    const v = input.value.trim();
    if (!v)                        return marcarCampo(input, helpId, false, `${etiqueta} es obligatorio`),       false;
    if (v.length < 2)              return marcarCampo(input, helpId, false, 'Mínimo 2 caracteres'),              false;
    if (!REGEX_SOLO_LETRAS.test(v)) return marcarCampo(input, helpId, false, 'Solo se permiten letras'),         false;
    marcarCampo(input, helpId, true);
    return true;
}

function validarCURP(input, helpId) {
    const v = input.value.trim().toUpperCase();
    input.value = v; // forzar mayúsculas
    if (!v)                      return marcarCampo(input, helpId, false, 'La CURP es obligatoria'),             false;
    if (v.length !== 18)         return marcarCampo(input, helpId, false, 'Debe tener exactamente 18 caracteres'), false;
    if (!REGEX_CURP.test(v))     return marcarCampo(input, helpId, false, 'Formato de CURP inválido'),           false;
    marcarCampo(input, helpId, true);
    return true;
}

function validarFechaNacimiento(input, helpId) {
    const v = input.value;
    if (!v) return marcarCampo(input, helpId, false, 'La fecha es obligatoria'), false;

    const fecha    = new Date(v + 'T00:00:00');
    const hoy      = new Date();
    const hace120  = new Date();
    hace120.setFullYear(hoy.getFullYear() - 120);

    if (fecha >= hoy)   return marcarCampo(input, helpId, false, 'La fecha no puede ser futura'),               false;
    if (fecha < hace120) return marcarCampo(input, helpId, false, 'Fecha fuera de rango permitido'),            false;

    // Calcular edad
    let edad = hoy.getFullYear() - fecha.getFullYear();
    const m  = hoy.getMonth() - fecha.getMonth();
    if (m < 0 || (m === 0 && hoy.getDate() < fecha.getDate())) edad--;

    marcarCampo(input, helpId, true);
    const helpEl = document.getElementById(helpId);
    if (helpEl) helpEl.textContent = `✓ Edad: ${edad} años`;
    return true;
}

function validarTipoSangre(select, helpId) {
    const v = select.value;
    if (!v) return marcarCampo(select, helpId, false, 'Selecciona tu tipo de sangre'), false;
    marcarCampo(select, helpId, true);
    return true;
}

function validarTelefono(input, helpId) {
    const v = input.value.replace(/\D/g, ''); // solo dígitos
    input.value = v;
    if (!v)          return marcarCampo(input, helpId, false, 'El teléfono es obligatorio'),                    false;
    if (v.length !== 10) return marcarCampo(input, helpId, false, 'Debe tener exactamente 10 dígitos'),         false;
    marcarCampo(input, helpId, true);
    return true;
}

function validarCorreo(input, helpId) {
    const v = input.value.trim();
    if (!v)                    return marcarCampo(input, helpId, false, 'El correo es obligatorio'),            false;
    if (!REGEX_EMAIL.test(v))  return marcarCampo(input, helpId, false, 'Formato de correo inválido'),          false;
    marcarCampo(input, helpId, true);
    return true;
}

function validarUsuarioRegistro(input, helpId) {
    const v = input.value.trim();
    if (!v)          return marcarCampo(input, helpId, false, 'El nombre de usuario es obligatorio'),           false;
    if (v.length < 4) return marcarCampo(input, helpId, false, 'Mínimo 4 caracteres'),                         false;
    if (v.length > 20) return marcarCampo(input, helpId, false, 'Máximo 20 caracteres'),                       false;
    if (/\s/.test(v)) return marcarCampo(input, helpId, false, 'No se permiten espacios'),                     false;
    if (!/^[a-zA-Z0-9._-]+$/.test(v))
        return marcarCampo(input, helpId, false, 'Solo letras, números, puntos, guiones y _'),                  false;
    marcarCampo(input, helpId, true);
    return true;
}

function validarPasswordRegistro(input, helpId) {
    const v = input.value;
    if (!v)           return marcarCampo(input, helpId, false, 'La contraseña es obligatoria'),                 false;
    if (v.length < 6) return marcarCampo(input, helpId, false, 'Mínimo 6 caracteres'),                         false;
    if (v.length > 50) return marcarCampo(input, helpId, false, 'Máximo 50 caracteres'),                       false;

    // Indicador de fortaleza
    const tieneMinuscula = /[a-z]/.test(v);
    const tieneMayuscula = /[A-Z]/.test(v);
    const tieneNumero    = /\d/.test(v);
    const tieneEspecial  = /[^a-zA-Z0-9]/.test(v);
    const fortaleza = [tieneMinuscula, tieneMayuscula, tieneNumero, tieneEspecial]
                        .filter(Boolean).length;

    const helpEl = document.getElementById(helpId);
    const etiquetas = ['', 'Débil', 'Regular', 'Buena', 'Fuerte'];
    const colores   = ['', '#dc3545', '#fd7e14', '#ffc107', '#28a745'];

    input.classList.remove('campo-invalido');
    input.classList.add('campo-valido');
    if (helpEl) {
        helpEl.textContent = `✓ Contraseña ${etiquetas[fortaleza]}`;
        helpEl.style.color = colores[fortaleza];
    }
    return true;
}

function validarConfirmarPassword(inputConfirm, helpId, inputOriginal) {
    const v1 = inputOriginal.value;
    const v2 = inputConfirm.value;
    if (!v2)    return marcarCampo(inputConfirm, helpId, false, 'Confirma tu contraseña'),                      false;
    if (v1 !== v2) return marcarCampo(inputConfirm, helpId, false, 'Las contraseñas no coinciden'),             false;
    marcarCampo(inputConfirm, helpId, true);
    const helpEl = document.getElementById(helpId);
    if (helpEl) helpEl.textContent = '✓ Las contraseñas coinciden';
    return true;
}


// ── Toggle visibilidad de contraseña ─────────────────────────────────────────

function setupToggle(campoId, botonId) {
    const campo = document.getElementById(campoId);
    const boton = document.getElementById(botonId);
    if (!campo || !boton) return;

    boton.addEventListener('click', () => {
        const esPassword = campo.type === 'password';
        campo.type = esPassword ? 'text' : 'password';
        boton.classList.toggle('fa-eye',      !esPassword);
        boton.classList.toggle('fa-eye-slash', esPassword);
    });
}


// ── Añadir span de ayuda dinámicamente si no existe ──────────────────────────

function asegurarHelpSpan(input, helpId, textoDefault = '') {
    if (document.getElementById(helpId)) return;
    const span = document.createElement('span');
    span.id = helpId;
    span.className = 'help-text';
    span.textContent = textoDefault;
    input.closest('.grupo-entrada')?.appendChild(span);
}


// ── Página de registro ────────────────────────────────────────────────────────

function initRegistro() {
    const ancla = document.getElementById('registroData');
    if (!ancla) return;

    // ── Obtener campos ──────────────────────────────────────────────────────
    const campos = {
        nombre:            document.querySelector('[name="nombre"]'),
        apellidoPaterno:   document.querySelector('[name="apellido_paterno"]'),
        apellidoMaterno:   document.querySelector('[name="apellido_materno"]'),
        curp:              document.querySelector('[name="curp"]'),
        fechaNacimiento:   document.querySelector('[name="fecha_nacimiento"]'),
        tipoSangre:        document.querySelector('[name="tipo_sangre"]'),
        telefono:          document.querySelector('[name="telefono"]'),
        correo:            document.querySelector('[name="correo"]'),
        usuario:           document.querySelector('[name="usuario"]'),
        password:          document.getElementById('campoPassword'),
        confirmar:         document.getElementById('campoConfirmarPassword'),
    };

    // ── Asegurar spans de ayuda ─────────────────────────────────────────────
    const helps = {
        nombre:          'nombreHelp',
        apellidoPaterno: 'apellidoPaternoHelp',
        apellidoMaterno: 'apellidoMaternoHelp',
        curp:            'curpHelp',
        fechaNacimiento: 'fechaNacimientoHelp',
        tipoSangre:      'tipoSangreHelp',
        telefono:        'telefonoHelp',
        correo:          'correoHelp',
        usuario:         'usuarioHelp',
        password:        'passwordHelp',
        confirmar:       'confirmarHelp',
    };

    Object.entries(campos).forEach(([key, el]) => {
        if (el) asegurarHelpSpan(el, helps[key]);
    });

    // ── Configurar toggles de contraseña ───────────────────────────────────
    setupToggle('campoPassword', 'btnAlternarPassword');
    setupToggle('campoConfirmarPassword', 'btnAlternarConfirmar');

    // ── Solo permitir dígitos en teléfono ──────────────────────────────────
    campos.telefono?.addEventListener('input', () => {
        campos.telefono.value = campos.telefono.value.replace(/\D/g, '').slice(0, 10);
    });

    // ── Solo permitir letras en nombre/apellidos ───────────────────────────
    [campos.nombre, campos.apellidoPaterno, campos.apellidoMaterno].forEach(campo => {
        campo?.addEventListener('input', () => {
            campo.value = campo.value.replace(/[^a-záéíóúüñA-ZÁÉÍÓÚÜÑ\s'-]/g, '');
        });
    });

    // ── Forzar CURP en mayúsculas ──────────────────────────────────────────
    campos.curp?.addEventListener('input', () => {
        campos.curp.value = campos.curp.value.toUpperCase();
    });

    // ── Eventos blur (validación al salir del campo) ───────────────────────
    campos.nombre?.addEventListener('blur',          () => validarNombre(campos.nombre, helps.nombre));
    campos.apellidoPaterno?.addEventListener('blur', () => validarApellido(campos.apellidoPaterno, helps.apellidoPaterno, 'El apellido paterno'));
    campos.apellidoMaterno?.addEventListener('blur', () => validarApellido(campos.apellidoMaterno, helps.apellidoMaterno, 'El apellido materno'));
    campos.curp?.addEventListener('blur',            () => validarCURP(campos.curp, helps.curp));
    campos.fechaNacimiento?.addEventListener('blur', () => validarFechaNacimiento(campos.fechaNacimiento, helps.fechaNacimiento));
    campos.tipoSangre?.addEventListener('change',    () => validarTipoSangre(campos.tipoSangre, helps.tipoSangre));
    campos.telefono?.addEventListener('blur',        () => validarTelefono(campos.telefono, helps.telefono));
    campos.correo?.addEventListener('blur',          () => validarCorreo(campos.correo, helps.correo));
    campos.usuario?.addEventListener('blur',         () => validarUsuarioRegistro(campos.usuario, helps.usuario));
    campos.password?.addEventListener('input',       () => {
        validarPasswordRegistro(campos.password, helps.password);
        // Re-validar confirmar si ya tiene valor
        if (campos.confirmar?.value) validarConfirmarPassword(campos.confirmar, helps.confirmar, campos.password);
    });
    campos.confirmar?.addEventListener('blur',       () => validarConfirmarPassword(campos.confirmar, helps.confirmar, campos.password));

    // ── Validación al enviar el formulario ────────────────────────────────
    const form = ancla.closest('form') ?? document.querySelector('form[action*="registro"]');
    const btnSubmit = form?.querySelector('[type="submit"]');

    form?.addEventListener('submit', (e) => {
        // Ejecutar todas las validaciones
        const resultados = [
            validarNombre(campos.nombre, helps.nombre),
            validarApellido(campos.apellidoPaterno, helps.apellidoPaterno, 'El apellido paterno'),
            validarApellido(campos.apellidoMaterno, helps.apellidoMaterno, 'El apellido materno'),
            validarCURP(campos.curp, helps.curp),
            validarFechaNacimiento(campos.fechaNacimiento, helps.fechaNacimiento),
            validarTipoSangre(campos.tipoSangre, helps.tipoSangre),
            validarTelefono(campos.telefono, helps.telefono),
            validarCorreo(campos.correo, helps.correo),
            validarUsuarioRegistro(campos.usuario, helps.usuario),
            validarPasswordRegistro(campos.password, helps.password),
            validarConfirmarPassword(campos.confirmar, helps.confirmar, campos.password),
        ];

        const todoValido = resultados.every(Boolean);

        if (!todoValido) {
            e.preventDefault();
            mostrarMensaje('error', 'Por favor corrige los errores antes de continuar');

            // Scroll al primer campo inválido
            const primerError = form.querySelector('.campo-invalido');
            primerError?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            // Deshabilitar botón para evitar doble envío
            if (btnSubmit) {
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = 'Registrando... <i class="fa-solid fa-spinner fa-spin"></i>';
            }
        }
    });

    // ── Mensajes del servidor (Flask) ─────────────────────────────────────
    const data = ancla.dataset;
    if (data.error)   mostrarMensaje('error', data.error);
    if (data.success) mostrarMensaje('exito', data.success);
}

// Solo se activa si estamos en la página de registro
if (document.getElementById('registroData')) {
    document.addEventListener('DOMContentLoaded', initRegistro);
}


// ── Página de login ───────────────────────────────────────────────────────────

function mostrarMensajeLogin(tipo, mensaje) {
    mostrarMensaje(tipo, mensaje); // reutiliza la función general
}

function setupTogglePassword() {
    setupToggle('campoPassword', 'btnAlternarPassword');
}

function setupValidaciones() {
    const usuarioInput  = document.getElementById('usuario');
    const passwordInput = document.getElementById('campoPassword');
    const loginForm     = document.getElementById('loginForm');
    const btnIngresar   = document.getElementById('btnIngresar');
    if (!loginForm) return;

    const validarUsuario = () => {
        const v = usuarioInput.value.trim();
        if (!v)         return marcarCampo(usuarioInput, 'usuarioHelp', false, 'El usuario o correo es obligatorio'), false;
        if (v.length < 3) return marcarCampo(usuarioInput, 'usuarioHelp', false, 'Mínimo 3 caracteres'),              false;
        marcarCampo(usuarioInput, 'usuarioHelp', true);
        return true;
    };

    const validarPassword = () => {
        const v = passwordInput.value;
        if (!v)           return marcarCampo(passwordInput, 'passwordHelp', false, 'La contraseña es obligatoria'),   false;
        if (v.length < 6) return marcarCampo(passwordInput, 'passwordHelp', false, 'Mínimo 6 caracteres'),            false;
        marcarCampo(passwordInput, 'passwordHelp', true);
        return true;
    };

    usuarioInput.addEventListener('input', validarUsuario);
    usuarioInput.addEventListener('blur',  validarUsuario);
    passwordInput.addEventListener('input', validarPassword);
    passwordInput.addEventListener('blur',  validarPassword);

    loginForm.addEventListener('submit', (e) => {
        const ok = validarUsuario() & validarPassword();
        if (!ok) {
            e.preventDefault();
            mostrarMensaje('error', 'Por favor corrige los errores antes de continuar');
            document.querySelector('.campo-invalido')
                    ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            btnIngresar.disabled = true;
            btnIngresar.innerHTML = 'Verificando... <i class="fa-solid fa-spinner fa-spin"></i>';
        }
    });
}

function initLogin() {
    const data = document.getElementById('loginData')?.dataset;
    if (!data) return;

    setupTogglePassword();
    setupValidaciones();

    if (data.error)   mostrarMensaje('error',  data.error);
    if (data.success) mostrarMensaje('exito',  data.success);
}

if (document.getElementById('loginData')) {
    document.addEventListener('DOMContentLoaded', initLogin);
}
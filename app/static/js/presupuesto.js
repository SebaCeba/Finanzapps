window.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".añadir-categoria").forEach(boton => {
        boton.addEventListener("click", function (e) {
            e.preventDefault();
            const form = boton.closest("form");
            const nuevaFila = form.querySelector(".nueva-fila");
            nuevaFila.style.display = "table-row";

            const inputNombre = nuevaFila.querySelector("input[name='nueva_categoria']");
            inputNombre.focus();

            inputNombre.onkeydown = null;

            inputNombre.addEventListener("keydown", function (ev) {
                if (ev.key === "Enter") {
                    ev.preventDefault();
                    form.requestSubmit();
                }
            });

            inputNombre.addEventListener("blur", () => {
                if (!inputNombre.value.trim()) {
                    nuevaFila.style.display = "none";
                    inputNombre.value = "";
                }
            });
        });
    });

    // Guardar todos los bloques
    const botonGuardarTodos = document.getElementById("guardar-todos");
    if (botonGuardarTodos) {
        botonGuardarTodos.addEventListener("click", async function (e) {
            e.preventDefault();
            const formularios = document.querySelectorAll(".form-bloque");
            let ok = true;

            for (const form of formularios) {
                const data = new FormData(form);
                try {
                    const resp = await fetch(form.action, {
                        method: form.method,
                        body: data
                    });
                    if (!resp.ok) ok = false;
                } catch {
                    ok = false;
                }
            }

            if (ok) {
                location.reload();
            } else {
                alert("Ocurrió un error al guardar. Intenta nuevamente.");
            }
        });
    }
});
inputNombre.addEventListener("keydown", function(ev) {
    if (ev.key === "Enter") {
        ev.preventDefault();
        const nuevoNombre = inputNombre.value.trim();
        if (!nuevoNombre) return;

        // Renombra los name de inputs presupuestarios
        const inputPpto = nuevaFila.querySelector("input[name='presupuesto[nueva_categoria]']");
        inputPpto.name = `presupuesto[${nuevoNombre}][1]`;  // ejemplo: mes 1 (o ajustable)

        inputNombre.name = `presupuesto[${nuevoNombre}][nombre]`;

        saveActiveInput();
        form.requestSubmit();
    }
});

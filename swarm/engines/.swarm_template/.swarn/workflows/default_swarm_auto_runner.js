const fs = require('fs');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function runStep(stepName, nextStep) {
  console.log(`--- Ejecutando paso: ${stepName} ---`);
  
  rl.question(`¿El paso ${stepName} ha sido validado correctamente? (Y/N): `, (answer) => {
    if (answer.toUpperCase() === 'Y') {
      console.log(`Paso ${stepName} completado. Preparando ${nextStep}...`);
      // Lógica para invocar siguiente agente
      process.exit(0);
    } else {
      console.log('Proceso detenido por el usuario.');
      process.exit(1);
    }
  });
}

// Ejemplo de inicio
runStep('M1-Ingenieria-Inversa', 'M2-BSP');

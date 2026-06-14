const fs = require('fs');
const path = require('path');

function bootstrapProject(projectName) {
  const root = process.cwd();
  const dirs = ['.swarm/states', '.swarm/logs', '.swarm/specs', 'bsp', 'architecture', 'src', 'docs'];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  });

  // Inicializar Board desde template
  const boardTemplate = fs.readFileSync(path.resolve(__dirname, '../specs/BOARD.md'), 'utf8');
  fs.writeFileSync(path.join(root, '.swarn/specs/BOARD.md'), boardTemplate);

  // Inicializar Manifest
  const manifest = { project: projectName, status: 'INITIALIZED', created: new Date() };
  fs.writeFileSync(path.join(root, '.swarn/specs/project_manifest.json'), JSON.stringify(manifest, null, 2));

  console.log(`Proyecto ${projectName} inicializado exitosamente.`);
}

const projectName = process.argv[2] || 'NewProject';
bootstrapProject(projectName);

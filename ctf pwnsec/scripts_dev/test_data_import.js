const path = 'data:text/javascript,console.log("PWNED BY DYNAMIC IMPORT!")//';
const name = 'test';
import(path + name + '.js')
  .then(() => console.log('Successfully imported!'))
  .catch(err => console.error('Import failed:', err));

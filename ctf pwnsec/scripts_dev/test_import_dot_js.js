import('data:text/javascript,import("data:text/javascript,console.log(1337)").js')
  .then(() => console.log('Outer promise resolved!'))
  .catch(err => console.error('Outer error:', err));

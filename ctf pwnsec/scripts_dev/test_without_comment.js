import('data:text/javascript,console.log("EXECUTED WITHOUT COMMENT!").js')
  .then(() => console.log('Promise resolved!'))
  .catch(err => console.error('Error:', err));

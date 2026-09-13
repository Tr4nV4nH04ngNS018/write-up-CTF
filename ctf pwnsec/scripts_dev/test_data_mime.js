// Test 1: data:, vs data:text/javascript, in dynamic import
async function test() {
  try {
    await import('data:,console.log("data: without mime works!")');
  } catch (e) {
    console.log('data:, failed:', e.message);
  }

  try {
    await import('data:text/javascript,console.log("data:text/javascript works!")');
  } catch (e) {
    console.log('data:text/javascript failed:', e.message);
  }
}
test();

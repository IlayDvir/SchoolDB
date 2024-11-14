document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('employeeButton').addEventListener('click', function() {
    window.location.href = '/employee-login';  // Route name, not file
  });

  document.getElementById('studentButton').addEventListener('click', function() {
    window.location.href = '/student-login';  // Route name, not file
  });
});
const form = document.getElementById('todo-form');
const input = document.getElementById('todo-input');
const list = document.getElementById('todo-list');

const tasks = [];

function renderTasks() {
  list.innerHTML = '';

  tasks.forEach((task, index) => {
    const item = document.createElement('li');
    item.className = `todo-item ${task.completed ? 'completed' : ''}`;

    const text = document.createElement('span');
    text.textContent = task.title;
    text.role = 'button';
    text.tabIndex = 0;
    text.title = 'Click to toggle complete';

    text.addEventListener('click', () => {
      task.completed = !task.completed;
      renderTasks();
    });

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.textContent = 'Delete';
    removeBtn.addEventListener('click', () => {
      tasks.splice(index, 1);
      renderTasks();
    });

    item.append(text, removeBtn);
    list.append(item);
  });
}

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const title = input.value.trim();
  if (!title) return;

  tasks.push({ title, completed: false });
  input.value = '';
  renderTasks();
});

renderTasks();

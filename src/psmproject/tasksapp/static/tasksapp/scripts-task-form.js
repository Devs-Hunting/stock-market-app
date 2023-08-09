const skills = JSON.parse(document.getElementById('skills').textContent);
const filterInput = document.getElementById('filter-skills');
const taskSkillPrefix = "task-skill-";
const skillPrefix = "pos-skill-";
const taskSkillList = document.getElementById("task-skills-list");
const skillList = document.getElementById("pos-skills-list");


function renderSkill(skill, idPrefix, onClick, parent){
        const skillSpan = document.createElement("span");
        skillSpan.id = idPrefix+skill.id;
        skillSpan.classList.add("badge");
        skillSpan.classList.add("text-bg-primary");
        skillSpan.classList.add("ms-1");
        skillSpan.innerHTML = skill.skill;
        skillSpan.onclick = onClick;
        parent.appendChild(skillSpan);
}

function removeSkill(skill, idPrefix, parent){
    const skill_el = document.getElementById(idPrefix+skill.id);
    parent.removeChild(skill_el);
}

function selectSkill(skill){
    renderSkill(skill, taskSkillPrefix, ()=>deselectSkill(skill), taskSkillList);
    removeSkill(skill, skillPrefix, skillList);
    const index = skills.findIndex(item => item.id === skill.id);
    console.log(index);
    console.log(skills);
    skills.splice(index, 1);
}

function deselectSkill(skill){
    renderSkill(skill, skillPrefix, ()=>selectSkill(skill), skillList);
    removeSkill(skill, taskSkillPrefix, taskSkillList);
    skills.push(skill);
}

function displayList(skills, filter){
    skillList.innerHTML = '';
    if (filter.length > 0) {
        const results = skills.filter(obj => {
            return obj.skill.toLowerCase().includes(filter.toLowerCase());
        });

        for (const skill of results) {
            renderSkill(skill, skillPrefix, ()=>selectSkill(skill), skillList);
        }
    }
}

const filterHandler = function(e) {
    displayList(skills, e.target.value);
}

filterInput.addEventListener('input', filterHandler);

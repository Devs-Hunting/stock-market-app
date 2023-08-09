const skills = JSON.parse(document.getElementById('skills').textContent);

const taskSkillPrefix = JSON.parse(document.getElementById('skillPrefix').textContent);
const skillPrefix = "pos-skill-";

const filterInput = document.getElementById('filter-skills');
const taskSkillList = document.getElementById("task-skills-list");
const skillList = document.getElementById("pos-skills-list");


function renderSkillForm(skill, idPrefix, onClick, parent){
        const skillButton = document.createElement("button");
        skillButton.id = idPrefix+skill.id;
        skillButton.innerHTML = skill.skill;
        skillButton.onclick = onClick;
        skillButton.classList.add("btn");
        skillButton.classList.add("btn-primary");
        skillButton.classList.add("btn-sm");
        skillButton.classList.add("ms-1");

        const skillInput = document.createElement("input");
        skillInput.name = idPrefix+skill.id;
        skillInput.type = "hidden";
        skillInput.value = skill.skill;

        skillButton.appendChild(skillInput);
        parent.appendChild(skillButton);
}

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
    renderSkillForm(skill, taskSkillPrefix, ()=>deselectSkill(skill), taskSkillList);
    removeSkill(skill, skillPrefix, skillList);
    const index = skills.findIndex(item => item.id === skill.id);
    skills.splice(index, 1);
}

function deselectSkill(skill){
    removeSkill(skill, taskSkillPrefix, taskSkillList);
    skills.push(skill);
    displayList(skills, filterInput.value)
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

function addOnClickToExistingSkills(parent){
    const buttons_el = parent.getElementsByTagName("button");
    const buttons_el_arr = [ ...buttons_el ];
    for (const button of buttons_el_arr) {
        const input = button.getElementsByTagName("input")[0];
        const skill_obj = {"id": button.id.replace(taskSkillPrefix, ""), "skill": input.value}
        button.onclick = () => deselectSkill(skill_obj);
    }
}

addOnClickToExistingSkills(taskSkillList);


const filterHandler = function(e) {
    displayList(skills, e.target.value);
}

filterInput.addEventListener('input', filterHandler);

class SkillManager {
    constructor() {
        this.skills = JSON.parse(document.getElementById('skills').textContent);
        this.taskSkillPrefix = JSON.parse(document.getElementById('skillPrefix').textContent);
        this.skillPrefix = "pos-skill-";
        this.filterInput = document.getElementById('filter-skills');
        this.taskSkillList = document.getElementById("task-skills-list");
        this.skillList = document.getElementById("pos-skills-list");
        this.initEventListeners();
    }

    renderSkillForm(skill, idPrefix, onClick, parent) {
        const skillButton = document.createElement("button");
        skillButton.id = idPrefix + skill.id;
        skillButton.innerHTML = skill.skill;
        skillButton.onclick = onClick;
        skillButton.classList.add("btn", "btn-primary", "btn-sm", "ms-1");

        const skillInput = document.createElement("input");
        skillInput.name = idPrefix + skill.id;
        skillInput.type = "hidden";
        skillInput.value = skill.skill;

        skillButton.appendChild(skillInput);
        parent.appendChild(skillButton);
    }

    renderSkill(skill, idPrefix, onClick, parent) {
        const skillSpan = document.createElement("span");
        skillSpan.id = idPrefix + skill.id;
        skillSpan.classList.add("badge", "text-bg-primary", "ms-1");
        skillSpan.innerHTML = skill.skill;
        skillSpan.onclick = onClick;
        parent.appendChild(skillSpan);
    }

    removeSkill(skill, idPrefix, parent) {
        const skill_el = document.getElementById(idPrefix + skill.id);
        parent.removeChild(skill_el);
    }

    selectSkill(skill) {
        this.renderSkillForm(skill, this.taskSkillPrefix, () => this.deselectSkill(skill), this.taskSkillList);
        this.removeSkill(skill, this.skillPrefix, this.skillList);
        const index = this.skills.findIndex(item => item.id === skill.id);
        this.skills.splice(index, 1);
    }

    deselectSkill(skill) {
        this.removeSkill(skill, this.taskSkillPrefix, this.taskSkillList);
        this.skills.push(skill);
        this.displayList(this.skills, this.filterInput.value);
    }

    displayList(skills, filter) {
        this.skillList.innerHTML = '';
        if (filter.length > 0) {
            const results = skills.filter(obj => {
                return obj.skill.toLowerCase().includes(filter.toLowerCase());
            });

            for (const skill of results) {
                this.renderSkill(skill, this.skillPrefix, () => this.selectSkill(skill), this.skillList);
            }
        }
    }

    addOnClickToExistingSkills(parent) {
        const buttons_el = parent.getElementsByTagName("button");
        const buttons_el_arr = [...buttons_el];
        for (const button of buttons_el_arr) {
            const input = button.getElementsByTagName("input")[0];
            const skill_obj = { "id": button.id.replace(this.taskSkillPrefix, ""), "skill": input.value }
            button.onclick = () => this.deselectSkill(skill_obj);
        }
    }

    initEventListeners() {
        this.addOnClickToExistingSkills(this.taskSkillList);
        this.filterInput.addEventListener('input', (e) => {
            this.displayList(this.skills, e.target.value);
        });
    }
}

const skillManager = new SkillManager();

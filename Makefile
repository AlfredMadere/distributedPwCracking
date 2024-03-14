launch-coordinator: 
	uvicorn src.coordination_launcher:app --reload

start-workers:
	python -m src.password_breaking_agent.start_workers

gen-pw:
	python -m src.gen_hashed_pw
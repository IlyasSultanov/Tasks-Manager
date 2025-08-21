from fastapi import APIRouter, Depends
from uuid import UUID
from service.service import TaskService
from schemas import schemas
from service.dep_service import get_task_service

router = APIRouter()


@router.post("/", response_model=schemas.Task)
async def create_task(
    task: schemas.TaskCreate, service: TaskService = Depends(get_task_service)
):
    return await service.create_task(task)


@router.get("/", response_model=list[schemas.Task])
async def get_tasks(
    skip: int = 0, limit: int = 100, service: TaskService = Depends(get_task_service)
):
    return await service.get_tasks(skip, limit)


@router.get("/{task_id}", response_model=schemas.Task)
async def get_task(task_id: UUID, service: TaskService = Depends(get_task_service)):
    return await service.get_task(task_id)


@router.put("/{task_id}", response_model=schemas.Task)
async def update_task(
    task_id: UUID,
    task_update: schemas.TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    return await service.update_task(task_id, task_update)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, service: TaskService = Depends(get_task_service)):
    return await service.delete_task(task_id)

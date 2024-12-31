from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry
from app.graphql.queries import Query
from app.graphql.mutations import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="FHIR Patient Server")
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "Welcome to FHIR Patient Server"} 

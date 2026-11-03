import Link from "next/link"

import { Badge } from "@workspace/ui/components/badge"
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card"

import { ORG_PATH, PROJECT_PATH } from "@/config/routes"

import type { Org, Project } from "../schemas"

/** Responsive grid shared by the organization and project lists. */
export function CardGrid({ children }: { children: React.ReactNode }) {
  return (
    <ul
      role="none"
      className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3"
    >
      {children}
    </ul>
  )
}

export function OrgCard({ org, projects }: { org: Org; projects: number }) {
  return (
    <li>
      <Link href={`${ORG_PATH}/${org.slug}`} className="block h-full">
        <Card className="h-full transition-colors duration-150 hover:bg-accent">
          <CardHeader>
            <CardTitle>{org.name}</CardTitle>
            <CardDescription className="font-mono">
              {projects} projects · {org.members} members
            </CardDescription>
            <Badge variant="secondary" className="w-fit">
              {org.plan}
            </Badge>
          </CardHeader>
        </Card>
      </Link>
    </li>
  )
}

export function ProjectCard({ project }: { project: Project }) {
  return (
    <li>
      <Link href={`${PROJECT_PATH}/${project.ref}`} className="block h-full">
        <Card className="h-full transition-colors duration-150 hover:bg-accent">
          <CardHeader>
            <CardTitle>{project.name}</CardTitle>
            <CardDescription className="font-mono">
              {project.ref} · {project.region}
            </CardDescription>
            <Badge
              variant={project.status === "active" ? "default" : "outline"}
              className="w-fit"
            >
              {project.status}
            </Badge>
          </CardHeader>
        </Card>
      </Link>
    </li>
  )
}

// physics_system.hpp
/*
  neogfx C++ GUI Library
  Copyright (c) 2018 Leigh Johnston.  All Rights Reserved.
  
  This program is free software: you can redistribute it and / or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#pragma once

#include <neogfx/neogfx.hpp>
#include <neogfx/game/system.hpp>

namespace neogfx::game
{
	class physics_system : public system
	{
	public:
		physics_system(const ecs::context& aContext);
	public:
		const system_id& id() const override;
		const neolib::i_string& name() const override;
	public:
		void apply() override;
	public:
		struct meta
		{
			static const neolib::uuid& id()
			{
				static const neolib::uuid sId = { 0x49443e26, 0x762e, 0x4517, 0xbbb8,{ 0xc3, 0xd6, 0x95, 0x7b, 0xe9, 0xd4 } };
				return sId;
			}
			static const neolib::i_string& name()
			{
				static const neolib::string sName = "Physics";
				return sName;
			}
		};
	};
}
// spliter.hpp
/*
  neogfx C++ GUI Library
  Copyright (c) 2015 Leigh Johnston.  All Rights Reserved.
  
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
#include <neogfx/gui/widget/widget.hpp>

namespace neogfx
{
    enum class splitter_type : uint32_t
    {
        None                = 0x0000,
        Horizontal          = 0x0001,
        Vertical            = 0x0002,
        ResizeSinglePane    = 0x1000
    };

    inline constexpr splitter_type operator|(splitter_type aLhs, splitter_type aRhs)
    {
        return static_cast<splitter_type>(static_cast<uint32_t>(aLhs) | static_cast<uint32_t>(aRhs));
    }

    inline constexpr splitter_type operator&(splitter_type aLhs, splitter_type aRhs)
    {
        return static_cast<splitter_type>(static_cast<uint32_t>(aLhs) & static_cast<uint32_t>(aRhs));
    }

    class splitter : public widget
    {
    private:
        typedef std::pair<uint32_t, uint32_t> separator_type;
    public:
        splitter(splitter_type aType = splitter_type::Horizontal);
        splitter(i_widget& aParent, splitter_type aType = splitter_type::Horizontal);
        splitter(i_layout& aLayout, splitter_type aType = splitter_type::Horizontal);
        ~splitter();
    public:
        i_widget& get_widget_at(const point& aPosition) override;
    public:
        neogfx::size_policy size_policy() const override;
    public:
        void mouse_button_pressed(mouse_button aButton, const point& aPosition, key_modifiers_e aKeyModifiers) override;
        void mouse_button_double_clicked(mouse_button aButton, const point& aPosition, key_modifiers_e aKeyModifiers) override;
        void mouse_moved(const point& aPosition, key_modifiers_e aKeyModifiers) override;
        void mouse_entered(const point& aPosition) override;
        void mouse_left() override;
        neogfx::mouse_cursor mouse_cursor() const override;
        void capture_released() override;
    public:
        virtual void panes_resized();
        virtual void reset_pane_sizes_requested(const std::optional<uint32_t>& aPane = std::optional<uint32_t>());
    private:
        std::optional<separator_type> separator_at(const point& aPosition) const;
    private:
        splitter_type iType;
        std::optional<separator_type> iTracking;
        std::pair<size, size> iSizeBeforeTracking;
        point iTrackFrom;
    };
}